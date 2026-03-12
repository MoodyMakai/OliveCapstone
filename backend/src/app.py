import logging
import mimetypes
import os
from dataclasses import asdict
from datetime import datetime

import aiosqlite
from quart import Quart, request
from quart.json import jsonify

from src.database import DatabaseManager

# Blueprint for email token verification
from src.service import StorageService
from src.storage import LocalFileStorage


class QuartApp(Quart):
    storage: StorageService  # Define storage explicitly to stop pyright from complaining


app = QuartApp(__name__)
app.config["DB_PATH"] = "database.sqlite"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Set up sqlite
def adapt_datetime(val):
    return val.isoformat()


def convert_datetime(val):
    return datetime.fromisoformat(val.decode())


aiosqlite.register_adapter(datetime, adapt_datetime)
aiosqlite.register_converter("timestamp", convert_datetime)


@app.route("/users/<email>", methods=["POST"])
async def create_user(email):
    data = await request.get_json()
    if not data or "email" not in data:
        logger.warning("Missing email data in create_user request")
        return jsonify({"error": "An email address is required."}), 400

    try:
        user_id = await app.storage.register_user(email=data["email"])
        if user_id is None:
            logger.warning(f"Failed to register user with email: {data['email']}")
            return jsonify({"error": "Invalid email address."}), 400
        logger.info(f"Successfully created user with ID: {user_id}")
        return jsonify({"message": "User successfully created.", "user_id": user_id}), 201
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        if "UNIQUE" in str(e).upper():
            return jsonify({"error": "A user with that email already exists."}), 400
        return jsonify({"error": "Internal server error occurred while creating user."}), 500


@app.route("/foodshares", methods=["GET"])
async def get_all_active_foodshares():
    foodshares = await app.storage.list_active_foodshares()
    foodshares = [asdict(f) for f in foodshares]
    return jsonify(foodshares), 200


@app.route("/foodshares", methods=["POST"])
async def add_foodshare():
    form = await request.form
    files = await request.files
    if not form or not files:
        return jsonify({"error": "Missing form data"}), 400

    picture = files.get("picture")
    if not picture:
        return jsonify({"error": "Missing picture file"}), 400

    try:
        name = form.get("name")
        location = form.get("location")
        ends = datetime.fromisoformat(str(form.get("ends")))
        active = form.get("active", "true").lower() == "true"
        user_id = form.get("user_id")
        if user_id is None:
            logger.warning("Missing user_id in add_foodshare request")
            raise TypeError
        else:
            try:
                user_id = int(user_id)
            except ValueError:
                return jsonify({"error": "Invalid user ID format"}), 400

        picture_expires = datetime.fromisoformat(str(form.get("picture_expires")))

        # Validate file extension and MIME type
        if not picture.filename:
            logger.warning("Missing filename in add_foodshare request")
            return jsonify({"error": "Invalid filename"}), 400

        # Extract extension and validate it
        extension = picture.filename.split(".")[-1].lower() if "." in picture.filename else "bin"

        # Whitelist allowed file extensions
        allowed_extensions = {"jpg", "jpeg", "png", "gif"}
        if extension not in allowed_extensions:
            logger.warning(f"Invalid file extension: {extension}")
            return jsonify(
                {
                    "error": """Invalid file type. Only JPG, JPEG, PNG,
                    and GIF files are allowed."""
                }
            ), 400

        # Validate MIME type based on extension
        mime_type, _ = mimetypes.guess_type(picture.filename)
        if not mime_type or not mime_type.startswith("image/"):
            logger.warning(f"Invalid MIME type for file: {picture.filename}")
            return jsonify({"error": "Invalid file type. Please upload an image file."}), 400

        # Validate file size (max 10MB)
        picture.stream.seek(0, os.SEEK_END)
        file_size = picture.stream.tell()
        if file_size > 10 * 1024 * 1024:  # 10MB
            logger.warning(f"File too large: {file_size} bytes")
            return jsonify({"error": "File too large. Maximum file size is 10MB."}), 400
        picture.stream.seek(0)  # Reset stream position

        if name is None or location is None:
            logger.warning("Missing name or location in add_foodshare request")
            raise TypeError

        foodshare_id = await app.storage.create_foodshare_with_picture(
            name=name,
            location=location,
            ends=ends,
            active=active,
            user_id=user_id,
            file_stream=picture.stream,
            extension=extension,
            mimetype=mime_type,
            picture_expires=picture_expires,
        )

        if foodshare_id:
            logger.info(f"Successfully created foodshare with ID: {foodshare_id}")
            return jsonify({"success": True, "foodshare_id": foodshare_id}), 201
        logger.error("Failed to create foodshare in database")
        return jsonify({"error": "Failed to create foodshare"}), 500

    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid data format in add_foodshare: {str(e)}")
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Unexpected error in add_foodshare: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error occurred while creating foodshare"}), 500


# runs before startup
@app.before_serving
async def startup():
    # Add the database manager to the app
    try:
        db = DatabaseManager(db_path=app.config["DB_PATH"])
        await db.connect()
        await db.init_tables()
        local_file_store = LocalFileStorage("images")
        app.storage = StorageService(db, local_file_store)
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}", exc_info=True)
        raise


@app.after_serving
async def shutdown():
    # Close the storage
    try:
        await app.storage.close()
        logger.info("Application shut down successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}", exc_info=True)


if __name__ == "__main__":
    app.run()
