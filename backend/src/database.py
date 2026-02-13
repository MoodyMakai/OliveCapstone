import re
from dataclasses import dataclass

import aiosqlite
from anyio import Path, open_file


@dataclass
class User:
    user_id: int
    email: str
    verified: bool = False
    banned: bool = False


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
    data = row.get("data")
    if picture_id is None or expires is None or data is None:
        return None
    return Picture(
        picture_id=int(picture_id),
        expires=str(expires),
        data=bytes(data),
    )


def validate_email_format(email: str) -> bool:
    # Regex explanation:
    # [^@\s]+: One or more characters that aren't '@' or whitespace
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
        schema_path = Path(__file__).parent / "schema.sql"
        if not self.conn:
            return
        async with await open_file(schema_path) as f:
            await self.conn.executescript(f.read())
        await self.conn.commit()

    # User functions

    async def add_user(self, email: str) -> bool:
        if not validate_email_format(email):
            return False
        await self.conn.execute(
            "INSERT INTO users (email, verified, banned) VALUES (?, 0, 0)"
        )
        await self.conn.commit()
        return True

    async def get_user_by_id(self, user_id: int) -> User | None:
        async with self.conn.execute(
            "SELECT * FROM users WHERE users.user_id = ?", user_id
        ) as cursor:
            row = await cursor.fetchone()
            if not isinstance(row, dict):
                return None
            return unpack_user_from_row(row)

    async def get_user_by_email(self, email: str) -> User | None:
        cursor = await self.conn.execute("SELECT * FROM users WHERE email = ?", email)
        row = await cursor.fetchone()
        if row is None:
            return None
        if not isinstance(row, dict):
            return None
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
        await self.conn.execute("DELETE FROM users where user_id = ?", user_id)
        await self.conn.commit()
