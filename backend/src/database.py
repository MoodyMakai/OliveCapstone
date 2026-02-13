import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import aiosqlite


@dataclass
class User:
    user_id: int
    email: str
    verified: bool = False
    banned: bool = False


@dataclass
class Picture:
    picture_id: int
    expires: datetime
    filepath: str
    mimetype: str


@dataclass
class Foodshare:
    foodshare_id: int
    location: str
    end_date: str
    active: bool
    user: User | None = None
    picture: Picture | None = None


@dataclass
class Survey:
    survey_id: int
    num_participants: int
    experience: int
    other_thoughts: str
    foodshare: Foodshare | None = None


# Helper functions for the database


def unpack_user_from_row(row: dict) -> User | None:
    if row is None:
        return None
    user_id = row.get("user_id")
    email = row.get("email")
    verified = row.get("verified")
    banned = row.get("banned")
    if user_id is None or email is None or verified is None or banned is None:
        return None
    return User(
        user_id=int(user_id),
        email=str(email),
        verified=bool(verified),
        banned=bool(banned),
    )


def unpack_picture_from_row(row: dict) -> Picture | None:
    if row is None:
        return None
    picture_id = row.get("picture_id")
    expires = row.get("expires")
    filepath = row.get("filepath")
    mimetype = row.get("mimetype")
    if picture_id is None or expires is None or filepath is None or mimetype is None:
        return None
    return Picture(
        picture_id=int(picture_id),
        expires=datetime.fromisoformat(expires),
        filepath=str(filepath),
        mimetype=str(mimetype),
    )


def validate_email_format(email: str) -> bool:
    # Regex explanation:
    # [^@\s]+: Matches one or more characters that aren't '@' or whitespace
    # @maine\.edu: Matches the literal characters: @maine.edu
    regex = r"[^@\s]+@maine\.edu"
    if re.fullmatch(regex, email, re.IGNORECASE):
        return True
    else:
        return False


class DatabaseManager:
    def __init__(self, db_path: str) -> None:
        self.db_path: str = db_path

    async def connect(self):
        # Connect to the database
        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row  # Returns dicts by default

        # Set config options
        await self.conn.execute("PRAGMA journal_mode=WAL")  # Helps concurrency
        await self.conn.execute("PRAGMA foreign_keys=ON")  # Enables foreign keys

    async def close(self):
        if self.conn:
            await self.conn.close()

    async def init_tables(self):
        queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                verified INTEGER,
                banned INTEGER
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS pictures (
                picture_id INTEGER PRIMARY KEY,
                expires TEXT NOT NULL,
                filepath TEXT NOT NULL,
                mimetype TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS foodshares (
                foodshare_id INTEGER PRIMARY KEY,
                location TEXT,
                end_date TEXT NOT NULL,
                active INTEGER,
                creator_id INTEGER REFERENCES users(user_id),
                picture_fk_id INTEGER REFERENCES pictures(picture_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS surveys (
                survey_id INTEGER PRIMARY KEY,
                num_participants INTEGER,
                experience INTEGER,
                other_thoughts TEXT,
                foodshare_fk_id INTEGER REFERENCES foodshares(foodshare_id)
            );
            """,
        ]
        for query in queries:
            await self.conn.execute(query)
        await self.conn.commit()

    # User functions

    async def add_user(
        self, email: str, verified: bool = False, banned: bool = False
    ) -> int | None:
        if not validate_email_format(email):
            return None

        async with self.conn.execute(
            "INSERT INTO users (email, verified, banned) VALUES (?, ?, ?)",
            (email, int(verified), int(banned)),
        ) as cursor:
            user_id = cursor.lastrowid
            await self.conn.commit()
            return user_id

    async def get_user_by_id(self, user_id: int) -> User | None:
        async with self.conn.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            row = dict(row)
            return unpack_user_from_row(row)

    async def get_user_by_email(self, email: str) -> User | None:
        async with self.conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            row = dict(row)
            return unpack_user_from_row(row)

    async def update_user_verification(self, user_id: int, new_status: bool):
        new_verification = 1 if new_status else 0
        await self.conn.execute(
            "UPDATE users SET verified = ? WHERE user_id = ?",
            (new_verification, user_id),
        )
        await self.conn.commit()

    async def update_user_ban(self, user_id: int, new_status: bool):
        new_ban = 1 if new_status else 0
        await self.conn.execute(
            "UPDATE users SET banned = ? WHERE user_id = ?",
            (new_ban, user_id),
        )
        await self.conn.commit()

    async def delete_user_by_id(self, user_id: int):
        await self.conn.execute("DELETE FROM users where user_id = ?", (user_id,))
        await self.conn.commit()

    # Picture functions

    async def add_picture(
        self, expires: datetime, filepath: str, mimetype: str
    ) -> int | None:
        # sanity check if date is earlier than current date
        if expires < datetime.now():
            return None
        async with self.conn.execute(
            "INSERT INTO pictures (expires, filepath, mimetype) VALUES (?, ?, ?)",
            (expires, filepath, mimetype),
        ) as cursor:
            picture_id = cursor.lastrowid
            await self.conn.commit()
            return picture_id

    async def get_picture_by_id(self, picture_id: int) -> Picture | None:
        async with self.conn.execute(
            "SELECT * FROM pictures WHERE picture_id = ?", (picture_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            row = dict(row)
            return unpack_picture_from_row(row)

    # deletes picture from database (NOT on disk), do not call directly
    async def _delete_picture(self, picture_id: int):
        await self.conn.execute(
            "DELETE FROM pictures WHERE picture_id = ?", (picture_id,)
        )
        await self.conn.commit()

    async def safe_delete_picture(self, picture_id) -> bool:
        # Does a sanity check to make sure the picture is expired
        picture = await self.get_picture_by_id(picture_id)
        if picture is None:
            return False
        if picture.expires >= datetime.now():
            return False
        await self._delete_picture(picture_id)
        return True
