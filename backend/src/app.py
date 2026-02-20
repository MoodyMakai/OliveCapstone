from quart import Quart

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
