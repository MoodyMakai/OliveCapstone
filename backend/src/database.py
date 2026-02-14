from datetime import datetime

import aiosqlite

from src.database_helpers import (
    PictureMetadata,
    User,
    unpack_picture_from_row,
    unpack_user_from_row,
)


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
            CREATE TABLE IF NOT EXISTS picture (
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

    async def add_picture_metadata(
        self, expires: datetime, filepath: str, mimetype: str
    ) -> int | None:
        async with self.conn.execute(
            "INSERT INTO pictures (expires, filepath, mimetype) VALUES (?, ?, ?)",
            (expires, filepath, mimetype),
        ) as cursor:
            picture_id = cursor.lastrowid
            await self.conn.commit()
            return picture_id

    async def get_picture_metadata_by_id(
        self, picture_id: int
    ) -> PictureMetadata | None:
        async with self.conn.execute(
            "SELECT * FROM pictures WHERE picture_id = ?", (picture_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            row = dict(row)
            return unpack_picture_from_row(row)

    async def get_expired_pictures(self) -> list[PictureMetadata]:
        async with self.conn.execute(
            "SELECT * FROM pictures WHERE expires > ?", (datetime.now().isoformat(),)
        ) as cursor:
            rows = await cursor.fetchall()
            picture_list = []
            for row in rows:
                if row is None:
                    continue
                picture_dict = dict(row)
                picture_list.append(unpack_picture_from_row(picture_dict))
            return picture_list

    # deletes picture from database (NOT on disk), do not call directly
    async def delete_picture_metadata(self, picture_id: int):
        await self.conn.execute(
            "DELETE FROM pictures WHERE picture_id = ?", (picture_id,)
        )
        await self.conn.commit()
