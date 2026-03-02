from dataclasses import asdict
from datetime import datetime

from quart import Quart, request
from quart.json import jsonify

from src.database import DatabaseManager

# Blueprint for email token verification
from src.email_routes import verification_bp
from src.service import StorageService
from src.storage import LocalFileStorage


class QuartApp(Quart):
    storage: (
        StorageService  # Define storage explicitly to stop pyright from complaining
    )


app = QuartApp(__name__)
app.config["DB_PATH"] = "database.sqlite"
# Registers the blueprint for email Verification links
app.register_blueprint(verification_bp, url_prefix="/verify")


@app.route("/")
def hello_world():
    return "<p>Black Bear Foodshare</p>"


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
        user_id = int(form.get("user_id"))  # pyright: ignore[reportArgumentType]

        picture_expires = datetime.fromisoformat(str(form.get("picture_expires")))
        extension = (
            picture.filename.split(".")[-1] if "." in picture.filename else "bin"
        )
        mimetype = picture.mimetype

        foodshare_id = await app.storage.create_foodshare_with_picture(
            name=name,  # pyright: ignore[reportArgumentType]
            location=location,  # pyright: ignore[reportArgumentType]
            ends=ends,
            active=active,
            user_id=user_id,
            file_stream=picture.stream,
            extension=extension,
            mimetype=mimetype,
            picture_expires=picture_expires,
        )

        if foodshare_id:
            return jsonify({"success": True, "foodshare_id": foodshare_id}), 201
        return jsonify({"error": "Failed to create foodshare"}), 500

    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid data format: {str(e)}"}), 400


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
