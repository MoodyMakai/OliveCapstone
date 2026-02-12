import asyncio

import aiosqlite
from quart import Quart

from database import DatabaseManager

DB_PATH = "database.sqlite"


class QuartApp(Quart):
    db_conn: aiosqlite.Connection


app = QuartApp(__name__)


@app.route("/")
def hello_world():
    return "<p>Black Bear Foodshare</p>"


# runs before startup
@app.before_serving
async def startup():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row

    await db.execute("PRAGMA journal_mode=WAL")  # Helps concurrency
    app.db_conn = db
    manager = DatabaseManager(db)
    await manager.init_tables()


@app.after_serving
async def shutdown():
    await app.db_conn.close()


def get_database_manager():
    return DatabaseManager(app.db_conn)
