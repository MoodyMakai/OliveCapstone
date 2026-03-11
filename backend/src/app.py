import mimetypes
import os
from dataclasses import asdict
from datetime import datetime

from quart import Quart, request
from quart.json import jsonify

from src.database import DatabaseManager

# Blueprint for email token verification
from src.service import StorageService
from src.storage import LocalFileStorage


class QuartApp(Quart):
    storage: (
        StorageService  # Define storage explicitly to stop pyright from complaining
    )


app = QuartApp(__name__)
app.config["DB_PATH"] = "database.sqlite"


@app.route("/users/<email>", methods=["POST"])
async def create_user(email):
    data = await request.get_json()
    if not data or "email" not in data:
        return jsonify({"error": "An email address is required."}), 400

    try:
        user_id = await app.storage.register_user(email=data["email"])
        if user_id is None:
            return jsonify({"error": "Invalid email address."}), 400
        return jsonify(
            {"message": "User successfully created.", "user_id": user_id}
        ), 201
    except Exception as e:
        if "UNIQUE" in str(e):
            return jsonify({"error": "A user with that email already exists."}), 400
        return jsonify({"error": "Internal server error."}), 500


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
            raise TypeError
        else:
            user_id = int(user_id)

        picture_expires = datetime.fromisoformat(str(form.get("picture_expires")))

        # Validate file extension and MIME type
        if not picture.filename:
            return jsonify({"error": "Invalid filename"}), 400

        # Extract extension and validate it
        extension = (
            picture.filename.split(".")[-1].lower()
            if "." in picture.filename
            else "bin"
        )

        # Whitelist allowed file extensions
        allowed_extensions = {"jpg", "jpeg", "png", "gif"}
        if extension not in allowed_extensions:
            return jsonify(
                {
                    "error": """Invalid file type. Only JPG, JPEG, PNG,
                    and GIF files are allowed."""
                }
            ), 400

        # Validate MIME type based on extension
        mime_type, _ = mimetypes.guess_type(picture.filename)
        if not mime_type or not mime_type.startswith("image/"):
            return jsonify(
                {"error": "Invalid file type. Please upload an image file."}
            ), 400

        # Validate file size (max 10MB)
        picture.stream.seek(0, os.SEEK_END)
        file_size = picture.stream.tell()
        if file_size > 10 * 1024 * 1024:  # 10MB
            return jsonify({"error": "File too large. Maximum file size is 10MB."}), 400
        picture.stream.seek(0)  # Reset stream position

        if name is None or location is None:
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
            return jsonify({"success": True, "foodshare_id": foodshare_id}), 201
        return jsonify({"error": "Failed to create foodshare"}), 500

    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400
    except Exception as e:
        print(f"Unexpected error in add_foodshare: {e}")  # Log for debugging
        return jsonify({"error": "Internal server error"}), 500


# runs before startup
@app.before_serving
async def startup():
    # Add the database manager to the app
    db = DatabaseManager(db_path=app.config["DB_PATH"])
    await db.connect()
    await db.init_tables()
    local_file_store = LocalFileStorage("images")
    app.storage = StorageService(db, local_file_store)


@app.after_serving
async def shutdown():
    # Close the storage
    await app.storage.close()


if __name__ == "__main__":
    app.run()
