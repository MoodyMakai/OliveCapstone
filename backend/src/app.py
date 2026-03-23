"""Main application module for the Foodshare backend.

This module initializes and configures the Quart web application, handles
user registration, foodshare creation, and manages database operations
and file storage through the StorageService.

The application supports:
- User registration with email validation
- Foodshare creation with image uploads
- Database operations using SQLite
- Local file storage for images

Key features:
- RESTful API endpoints for user and foodshare management
- File validation for image uploads (type, size, format)
- Database schema initialization
- Proper error handling and logging

Attributes:
    app (QuartApp): The main Quart application instance with storage support
    logger: Application logger for tracking events and errors

Endpoints:
    POST /users/<email>: Create a new user
    GET /foodshares: Retrieve all active foodshares
    POST /foodshares: Add a new foodshare with associated image

Usage:
    Run directly to start the application server:
        python app.py

    The application will initialize database tables and set up storage
    during startup, then listen for incoming requests on the default port.
"""

import logging
import mimetypes
import os
from dataclasses import asdict
from datetime import datetime

import aiosqlite
from quart import g, request
from quart.json import jsonify
from quart_rate_limiter import RateLimiter

from src.auth_routes import auth_bp, require_admin, require_auth
from src.core import QuartApp
from src.database import DatabaseManager

# Blueprint for email token verification
from src.service import StorageService
from src.storage import LocalFileStorage

app = QuartApp(__name__)
app.config["DB_PATH"] = "database.sqlite"
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize RateLimiter only if not in testing mode to avoid global state issues in tests
if not app.config.get("TESTING"):
    rate_limiter = RateLimiter(app)


# Set up sqlite
def adapt_datetime(val):
    """Convert datetime object to ISO format string for database storage.

    Args:
        val (datetime): The datetime object to convert

    Returns:
        str: ISO format string representation of the datetime
    """
    return val.isoformat()


def convert_datetime(val):
    """Convert ISO format string back to datetime object.

    Args:
        val (bytes): The ISO format string to convert

    Returns:
        datetime: The converted datetime object
    """
    return datetime.fromisoformat(val.decode())


aiosqlite.register_adapter(datetime, adapt_datetime)
aiosqlite.register_converter("timestamp", convert_datetime)

app.register_blueprint(auth_bp)


@app.route("/users", methods=["POST"])
async def create_user():
    """Create a new user with the given email in the JSON payload.

    Returns:
        tuple: JSON response with success message and user ID or error message
    """
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
@require_auth
async def get_all_active_foodshares():
    """Retrieve all active foodshares from the database.

    Returns:
        tuple: JSON response with list of active foodshares or error message
    """
    foodshares = await app.storage.db.get_all_active_foodshares()
    foodshares = [asdict(f) for f in foodshares]
    return jsonify(foodshares), 200


@app.route("/foodshares", methods=["POST"])
@require_auth
async def add_foodshare():
    """Add a new foodshare with associated picture.

    Validates file type, size, and format before creating the foodshare.

    Returns:
        tuple: JSON response with success message and foodshare ID or error message
    """
    form = await request.form
    files = await request.files

    if not form and not files:
        return jsonify({"error": "Missing form data or files"}), 400

    picture = files.get("picture")
    if not picture:
        return jsonify({"error": "Missing picture file"}), 400

    try:
        name = form.get("name")
        location = form.get("location")

        if not name or not location:
            logger.warning("Missing name or location in add_foodshare request")
            return jsonify({"error": "Name and location are required."}), 400

        ends = datetime.fromisoformat(str(form.get("ends")))
        active = form.get("active", "true").lower() == "true"

        user_id = g.user.user_id

        picture_expires = datetime.fromisoformat(str(form.get("picture_expires")))

        # Validate file extension and MIME type
        if not picture.filename:
            logger.warning("Missing filename in add_foodshare request")
            return jsonify({"error": "Invalid filename"}), 400

        # Extract original metadata (extension and mimetype are updated during processing)
        extension = picture.filename.split(".")[-1].lower() if "." in picture.filename else "bin"
        mime_type, _ = mimetypes.guess_type(picture.filename)

        # Basic mime check to ensure it's an image
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

        # Create the foodshare (processing handles conversion to optimized WebP)
        foodshare_id = await app.storage.create_foodshare_with_picture(
            name=name,
            location=location,
            ends=ends,
            active=active,
            user_id=user_id,
            file_stream=picture.read(),  # Read the full stream for Pillow
            extension=extension,
            mimetype=mime_type,
            picture_expires=picture_expires,
        )

        if foodshare_id:
            logger.info(f"Successfully created foodshare ID {foodshare_id} by user {user_id}")
            return jsonify({"success": True, "foodshare_id": foodshare_id}), 201

        logger.error("Failed to create foodshare in database")
        return jsonify({"error": "Failed to create foodshare"}), 500

    except ValueError as e:
        logger.warning(f"Invalid date format in add_foodshare: {str(e)}")
        return jsonify({"error": "Invalid date format. Please use ISO format for dates."}), 400
    except Exception as e:
        logger.error(f"Unexpected error in add_foodshare: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error occurred while creating foodshare"}), 500


@app.route("/foodshares/close", methods=["POST"])
@require_auth
async def close_foodshare():
    """Closes a foodshare.

    Validates the user, ensures they are the creator of the foodshare,
    and sets the foodshare to inactive.

    Returns:
        tuple: JSON response with success message and foodshare ID or error message
    """
    try:
        data = await request.get_json()

        if not data or "foodshare_id" not in data:
            return jsonify({"error": "Missing 'foodshare_id' in request body"}), 400

        try:
            target_id = int(data["foodshare_id"])
        except ValueError:
            return jsonify({"error": "'foodshare_id' must be an integer"}), 400

        user = g.user

        foodshare = await app.storage.db.get_foodshare(target_id)

        if not foodshare:
            return jsonify({"error": "Foodshare not found"}), 404

        if not foodshare.creator or foodshare.creator.user_id != user.user_id:
            logger.warning(f"User {user.user_id} attempted to close foodshare {target_id} owned by someone else.")
            return jsonify({"error": "You do not have permission to close this foodshare"}), 403

        closed_id = await app.storage.db.deactivate_foodshare(target_id)

        if closed_id:
            logger.info(f"User {user.user_id} successfully closed foodshare with ID: {closed_id}")
            return jsonify({"success": True, "foodshare_id": closed_id}), 200

        return jsonify({"error": "Failed to close foodshare"}), 500

    except Exception as e:
        logger.error(f"Unexpected error in close_foodshare: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error occurred while closing foodshare"}), 500


@app.route("/surveys", methods=["POST"])
@require_auth
async def submit_survey():
    """Submit a new survey response.

    Expects a JSON payload with 'num_participants' and 'experience'.
    'other_thoughts' and 'foodshare_fk_id' are optional.

    Returns:
        tuple: JSON response with success message and survey ID or error message
    """
    try:
        data = await request.get_json()
        if not data:
            return jsonify({"error": "Missing JSON payload"}), 400

        # Check for required fields
        if "num_participants" not in data or "experience" not in data:
            return jsonify({"error": "Missing required fields: 'num_participants' and 'experience'"}), 400

        # Type-cast and validate required fields
        try:
            num_participants = int(data["num_participants"])
            experience = int(data["experience"])
        except ValueError:
            return jsonify({"error": "'num_participants' and 'experience' must be integers"}), 400

        # Handle optional fields
        other_thoughts = str(data.get("other_thoughts", ""))

        foodshare_fk_id = data.get("foodshare_fk_id")
        if foodshare_fk_id is not None:
            try:
                foodshare_fk_id = int(foodshare_fk_id)
            except ValueError:
                return jsonify({"error": "'foodshare_fk_id' must be an integer"}), 400

        # Save to the database
        survey_id = await app.storage.db.add_survey(
            num_participants=num_participants,
            experience=experience,
            other_thoughts=other_thoughts,
            foodshare_fk_id=foodshare_fk_id,
        )

        if survey_id:
            logger.info(f"User {g.user.user_id} successfully submitted survey ID: {survey_id}")
            return jsonify({"success": True, "survey_id": survey_id}), 201

        logger.error("Database returned None when creating survey.")
        return jsonify({"error": "Failed to submit survey"}), 500

    except Exception as e:
        logger.error(f"Unexpected error in submit_survey: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error occurred while submitting survey"}), 500


@app.route("/surveys", methods=["GET"])
@require_auth
@require_admin
async def get_all_surveys():
    """Retrieve all surveys from the database.

    Returns:
        tuple: JSON response with list of all surveys or error message
    """
    try:
        surveys = await app.storage.db.get_all_surveys()
        surveys_dict = [asdict(survey) for survey in surveys]

        return jsonify(surveys_dict), 200

    except Exception as e:
        logger.error(f"Unexpected error in get_all_surveys: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error occurred while retrieving surveys"}), 500


# runs before startup
@app.before_serving
async def startup():
    """Initialize the application before serving.

    Sets up database connection, initializes tables, and configures storage service.

    Raises:
        Exception: If there's an error during application initialization
    """
    # Add the storage service to the app
    try:
        db = DatabaseManager(db_path=app.config["DB_PATH"])
        await db.connect()
        await db.init_tables()
        upload_folder = app.config.get("UPLOAD_FOLDER", "images")
        local_file_store = LocalFileStorage(upload_folder)
        app.storage = StorageService(db, local_file_store)
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}", exc_info=True)
        raise


@app.after_serving
async def shutdown():
    """Clean up resources after the application stops serving.

    Closes the storage service connection.

    Raises:
        Exception: If there's an error during application shutdown
    """
    # Close the storage
    try:
        await app.storage.close()
        logger.info("Application shut down successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}", exc_info=True)


if __name__ == "__main__":
    """Run the application when executed directly."""
    app.run()
