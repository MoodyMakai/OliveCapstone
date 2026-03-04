from datetime import datetime

import aiosqlite

from src.database_helpers import (
    Foodshare,
    PictureMetadata,
    Survey,
    User,
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
                name TEXT,
                location TEXT,
                ends TEXT NOT NULL,
                active INTEGER,
                user_fk_id INTEGER REFERENCES users(user_id),
                picture_fk_id INTEGER REFERENCES pictures(picture_id)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS restrictions (
                restriction_id INTEGER PRIMARY KEY,
                label TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS foodshare_restrictions (
                foodshare_id INTEGER,
                restriction_id INTEGER,
                FOREIGN KEY(foodshare_id) REFERENCES foodshares(foodshare_id),
                FOREIGN KEY(restriction_id) REFERENCES restrictions(restriction_id),
                PRIMARY KEY (foodshare_id, restriction_id)
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
            """
            CREATE TABLE IF NOT EXISTS device_tokens (
                device_token TEXT NOT NULL
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
        query = """
            INSERT INTO users (email, verified, banned)
            VALUES (?, ?, ?)
        """
        cursor = await self.conn.execute(query, (email, int(verified), int(banned)))
        await self.conn.commit()
        return cursor.lastrowid

    async def get_user(self, user_id: int) -> User | None:
        query = "SELECT * FROM users WHERE user_id = ?"
        async with self.conn.execute(query, (user_id,)) as cursor:
            row = await cursor.fetchone()

        if row:
            return User(
                user_id=row["user_id"],
                email=row["email"],
                verified=bool(row["verified"]),
                banned=bool(row["banned"]),
            )
        return None

    async def get_user_by_email(self, email: str) -> User | None:
        query = "SELECT * FROM users WHERE email = ?"
        async with self.conn.execute(query, (email,)) as cursor:
            row = await cursor.fetchone()

        if row:
            return User(
                user_id=row["user_id"],
                email=row["email"],
                verified=bool(row["verified"]),
                banned=bool(row["banned"]),
            )
        return None

    async def update_user_status(
        self, user_id: int, verified: bool | None = None, banned: bool | None = None
    ) -> None:
        updates = []
        params = []
        if verified is not None:
            updates.append("verified = ?")
            params.append(int(verified))
        if banned is not None:
            updates.append("banned = ?")
            params.append(int(banned))

        if not updates:
            return

        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
        params.append(user_id)
        await self.conn.execute(query, tuple(params))
        await self.conn.commit()

    # aiosqlite is expecting a tuple, but is recieving an int
    async def delete_user_by_id(self, user_id: int):
        await self.conn.execute("DELETE FROM users where user_id = ?", (user_id,))
        await self.conn.commit()

    # Picture functions

    async def add_picture(
        self, expires: datetime, filepath: str, mimetype: str
    ) -> int | None:
        """Inserts picture metadata and returns the ID."""
        query = """
            INSERT INTO pictures (expires, filepath, mimetype)
            VALUES (?, ?, ?)
        """
        cursor = await self.conn.execute(
            query, (expires.isoformat(), filepath, mimetype)
        )
        await self.conn.commit()
        return cursor.lastrowid

    async def get_picture(self, picture_id: int) -> PictureMetadata | None:
        query = "SELECT * FROM pictures WHERE picture_id = ?"
        async with self.conn.execute(query, (picture_id,)) as cursor:
            row = await cursor.fetchone()

        if row:
            return PictureMetadata(
                picture_id=row["picture_id"],
                expires=datetime.fromisoformat(row["expires"]),
                filepath=row["filepath"],
                mimetype=row["mimetype"],
            )
        return None

    async def delete_expired_pictures(self) -> list[str]:
        now_iso = datetime.now().isoformat()
        select_query = "SELECT filepath FROM pictures WHERE expires < ?"
        async with self.conn.execute(select_query, (now_iso,)) as cursor:
            rows = await cursor.fetchall()
            filepaths_to_delete = [row["filepath"] for row in rows]

        if filepaths_to_delete:
            delete_query = "DELETE FROM pictures WHERE expires < ?"
            await self.conn.execute(delete_query, (now_iso,))
            await self.conn.commit()

        return filepaths_to_delete

    # Foodshare CRUD

    async def add_foodshare(
        self,
        name: str,
        location: str,
        ends: datetime,
        active: bool,
        user_fk_id: int | None = None,
        picture_fk_id: int | None = None,
    ) -> int | None:
        query = """
                INSERT INTO foodshares
                (name, location, ends, active, user_fk_id, picture_fk_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """
        cursor = await self.conn.execute(
            query,
            (name, location, ends.isoformat(), int(active), user_fk_id, picture_fk_id),
        )
        await self.conn.commit()
        return cursor.lastrowid

    async def link_foodshare_restriction(
        self, foodshare_id: int, restriction_id: int
    ) -> None:
        query = """
        INSERT OR IGNORE INTO foodshare_restrictions
        (foodshare_id, restriction_id) VALUES (?, ?)
        """
        await self.conn.execute(query, (foodshare_id, restriction_id))
        await self.conn.commit()

    async def get_foodshare(self, foodshare_id: int) -> Foodshare | None:
        query = "SELECT * FROM foodshares WHERE foodshare_id = ?"
        async with self.conn.execute(query, (foodshare_id,)) as cursor:
            fs_row = await cursor.fetchone()

        if not fs_row:
            return None

        creator = (
            await self.get_user(fs_row["user_fk_id"]) if fs_row["user_fk_id"] else None
        )
        picture = (
            await self.get_picture(fs_row["picture_fk_id"])
            if fs_row["picture_fk_id"]
            else None
        )

        restrictions_query = """
            SELECT r.label
            FROM restrictions r
            JOIN foodshare_restrictions fr ON r.restriction_id = fr.restriction_id
            WHERE fr.foodshare_id = ?
        """
        async with self.conn.execute(restrictions_query, (foodshare_id,)) as cursor:
            rest_rows = await cursor.fetchall()
            restrictions_list = [row["label"] for row in rest_rows]

        return Foodshare(
            foodshare_id=fs_row["foodshare_id"],
            name=fs_row["name"],
            location=fs_row["location"],
            ends=datetime.fromisoformat(fs_row["ends"]),
            restrictions=restrictions_list,
            active=bool(fs_row["active"]),
            creator=creator,
            picture=picture,
        )

    async def get_all_active_foodshares(self) -> list[Foodshare]:
        query = "SELECT foodshare_id FROM foodshares WHERE active = 1"
        async with self.conn.execute(query) as cursor:
            rows = await cursor.fetchall()

        active_foodshares = []
        for row in rows:
            foodshare = await self.get_foodshare(row["foodshare_id"])
            if foodshare:
                active_foodshares.append(foodshare)

        return active_foodshares

    # Survey CRUD

    async def add_survey(
        self,
        num_participants: int,
        experience: int,
        other_thoughts: str,
        foodshare_fk_id: int | None = None,
    ) -> int | None:
        """Inserts a new survey record."""
        query = """
                INSERT INTO surveys
                (num_participants, experience, other_thoughts, foodshare_fk_id)
                VALUES (?, ?, ?, ?)
            """
        cursor = await self.conn.execute(
            query, (num_participants, experience, other_thoughts, foodshare_fk_id)
        )
        await self.conn.commit()
        return cursor.lastrowid

    async def get_survey(self, survey_id: int) -> Survey | None:
        query = "SELECT * FROM surveys WHERE survey_id = ?"
        async with self.conn.execute(query, (survey_id,)) as cursor:
            row = await cursor.fetchone()

        if row:
            foodshare = (
                await self.get_foodshare(row["foodshare_fk_id"])
                if row["foodshare_fk_id"]
                else None
            )
            return Survey(
                survey_id=row["survey_id"],
                num_participants=row["num_participants"],
                experience=row["experience"],
                other_thoughts=row["other_thoughts"],
                foodshare=foodshare,
            )
        return None

    async def get_all_surveys(self) -> list["Survey"]:
        query = "SELECT survey_id FROM surveys"
        async with self.conn.execute(query) as cursor:
            rows = await cursor.fetchall()

        surveys = []
        for row in rows:
            survey = await self.get_survey(row["survey_id"])
            if survey:
                surveys.append(survey)
        return surveys
