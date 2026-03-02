from quart import Quart, request
from quart.json import jsonify

from src.database import DatabaseManager
from src.service import StorageService
from src.storage import LocalFileStorage


class QuartApp(Quart):
    storage: (
        StorageService  # Define storage explicitly to stop pyright from complaining
    )


app = QuartApp(__name__)
app.config["DB_PATH"] = "database.sqlite"


@app.route("/")
def hello_world():
    return "<p>Black Bear Foodshare</p>"


@app.route("/users/<email>", methods=["POST"])
async def create_user(email):
    data = await request.get_json()
    print(data)
    print(email)
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
