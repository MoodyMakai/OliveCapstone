from quart import Quart

from src.database import DatabaseManager

# Blueprint for email token verification
from src.email_routes import verification_bp


class QuartApp(Quart):
    db: DatabaseManager  # Define db explicitly to stop pyright from complaining


app = QuartApp(__name__)
app.config["DB_PATH"] = "database.sqlite"
# Registers the blueprint for email Verification links
app.register_blueprint(verification_bp, url_prefix="/verify")


@app.route("/")
def hello_world():
    return "<p>Black Bear Foodshare</p>"


# runs before startup
@app.before_serving
async def startup():
    # Add the database manager to the app
    app.db = DatabaseManager(db_path=app.config["DB_PATH"])
    await app.db.connect()
    await app.db.init_tables()


@app.after_serving
async def shutdown():
    # Close the database
    await app.db.close()


if __name__ == "__main__":
    app.run()
