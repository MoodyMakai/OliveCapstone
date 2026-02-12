import re
from dataclasses import dataclass
from tkinter.constants import FALSE
from typing import Optional

import aiosqlite


@dataclass
class User:
    user_id: int
    email: str
    verified: bool
    banned: bool


@dataclass
class Picture:
    picture_id: int
    expires: str
    data: bytes


@dataclass
class Foodshare:
    foodshare_id: int
    location: str
    end_date: str
    active: bool
    picture: Optional[Picture] = None


@dataclass
class Survey:
    survey_id: int
    num_participants: int
    experience: int
    other_thoughts: str
    foodshare: Optional[Foodshare] = None


# Helper functions for the database


def validate_email_format(email: str) -> bool:
    # Regex explanation:
    # [^@\s]+: One or more characters that aren't '@' or whitespace
    # @: Matches the '@' symbol
    # maine\.edu: Matches the literal characters: maine.edu
    regex = r"[^@\s]+@maine\.edu"
    if re.fullmatch(regex, email, re.IGNORECASE):
        return True
    else:
        return False


class DatabaseManager:
    def __init__(self, db_conn: aiosqlite.Connection) -> None:
        self.db: aiosqlite.Connection = db_conn

    async def init_tables(self):
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            verified INTEGER,
            banned INTEGER
            )
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS pictures (
            picture_id INTEGER PRIMARY KEY,
            expires TEXT NOT NULL,
            data BLOB NOT NULL
            )
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS foodshares (
            foodshare_id INTEGER PRIMARY KEY,
            creator_id REFERENCES users(user_id),
            location TEXT,
            picture_fk_id INTEGER REFERENCES pictures(picture_id),
            end_date TEXT NOT NULL,
            active INTEGER
            )
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS surveys (
            survey_id INTEGER PRIMARY KEY,
            foodshare_fk_id REFERENCES foodshares(foodshare_id),
            num_participants INTEGER,
            experience INTEGER,
            other_thoughts TEXT
            )
            """
        )
        await self.db.commit()

    # User functions

    async def add_user(self, email: str) -> bool:
        if not validate_email_format(email):
            return False
        await self.db.execute(
            "INSERT INTO users (email, verified, banned) VALUES (?, 0, 0)"
        )
        await self.db.commit()
        return True

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        cursor = await self.db.execute(
            "SELECT * FROM users WHERE users.user_id = ?", user_id
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return User(
            user_id=row["user_id"],
            email=row["email"],
            verified=bool(row["verified"]),
            banned=bool(row["banned"]),
        )

    async def get_user_by_email(self, email: str) -> Optional[User]:
        cursor = await self.db.execute("SELECT * FROM users WHERE email = ?", email)
        row = await cursor.fetchone()
        if row is None:
            return None
        return User(
            user_id=row["user_id"],
            email=row["email"],
            verified=bool(row["verified"]),
            banned=bool(row["banned"]),
        )

    async def update_user_verification(self, user_id: int, new_status: bool):
        new_verification = 1 if new_status else 0
        await self.db.execute(
            "UPDATE users SET verified = ? WHERE user_id = ?",
            (new_verification, user_id),
        )
        await self.db.commit()

    async def update_user_ban(self, user_id: int, new_status: bool):
        new_ban = 1 if new_status else 0
        await self.db.execute(
            "UPDATE users SET ban = ? WHERE user_id = ?",
            (new_ban, user_id),
        )
        await self.db.commit()

    async def delete_user_by_id(self, user_id: int):
        await self.db.execute("DELETE FROM users where user_id = ?", user_id)
        await self.db.commit()
