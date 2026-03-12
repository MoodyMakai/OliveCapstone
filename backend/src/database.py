import logging
from datetime import UTC, datetime

import aiosqlite
import anyio

from src.database_helpers import (
    DeviceSession,
    Foodshare,
    OTPRecord,
    PictureMetadata,
    Survey,
    User,
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path: str) -> None:
        self.db_path: str = db_path

    async def connect(self):
        # Connect to the database
        try:
            self.conn = await aiosqlite.connect(self.db_path, timeout=20.0)
            self.conn.row_factory = aiosqlite.Row  # Returns dicts by default

            # Set config options
            await self.conn.execute("PRAGMA journal_mode=WAL")  # Helps concurrency
            await self.conn.execute("PRAGMA foreign_keys=ON")  # Enables foreign keys
            await self.conn.execute("PRAGMA synchronous=NORMAL")  # Better performance
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}", exc_info=True)
            raise

    async def close(self):
        try:
            if self.conn:
                await self.conn.close()
                logger.info("Database connection closed successfully")
        except Exception as e:
            logger.error(f"Failed to close database connection: {str(e)}", exc_info=True)
            raise

    async def init_tables(self):
        try:
            current_dir = anyio.Path(__file__).parent

            sql_file_path = current_dir / "sql" / "init_tables.sql"

            async with await anyio.open_file(sql_file_path, "r") as sql_file:
                sql_content = await sql_file.read()
                await self.conn.executescript(sql_content)

            await self.conn.commit()
            logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database tables: {str(e)}", exc_info=True)
            raise

    # User functions

    async def add_user(self, email: str, verified: bool = False, banned: bool = False) -> int | None:
        try:
            query = """
                INSERT INTO users (email, verified, banned)
                VALUES (?, ?, ?)
            """
            cursor = await self.conn.execute(query, (email, int(verified), int(banned)))
            await self.conn.commit()
            user_id = cursor.lastrowid
            logger.info(f"User added successfully with ID: {user_id}")
            return user_id
        except Exception as e:
            logger.error(f"Failed to add user: {str(e)}", exc_info=True)
            raise

    async def get_user(self, user_id: int) -> User | None:
        try:
            query = "SELECT * FROM users WHERE user_id = ?"
            async with self.conn.execute(query, (user_id,)) as cursor:
                row = await cursor.fetchone()

            if row:
                user = User(
                    user_id=row["user_id"],
                    email=row["email"],
                    verified=bool(row["verified"]),
                    banned=bool(row["banned"]),
                )
                logger.debug(f"User retrieved successfully: {user_id}")
                return user
            logger.info(f"No user found with ID: {user_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {str(e)}", exc_info=True)
            raise

    async def get_user_by_email(self, email: str) -> User | None:
        try:
            query = "SELECT * FROM users WHERE email = ?"
            async with self.conn.execute(query, (email,)) as cursor:
                row = await cursor.fetchone()

            if row:
                user = User(
                    user_id=row["user_id"],
                    email=row["email"],
                    verified=bool(row["verified"]),
                    banned=bool(row["banned"]),
                )
                logger.debug(f"User retrieved successfully by email: {email}")
                return user
            logger.info(f"No user found with email: {email}")
            return None
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {str(e)}", exc_info=True)
            raise

    async def get_user_by_token(self, token: str) -> User | None:
        try:
            query = """
            SELECT u.user_id, u.email, u.verified, u.banned
            FROM device_tokens t, users u
            JOIN users u ON u.user_id = t.user_id
            WHERE t.token_hash = ?
            """
            async with self.conn.execute(query, (token,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    user = User(
                        user_id=row["user_id"],
                        email=row["email"],
                        verified=bool(row["verified"]),
                        banned=bool(row["banned"]),
                    )
                    logger.debug("User retrieved successfully by token")
                    return user
                logger.info("No user found with provided token")
                return None
        except Exception as e:
            logger.error(f"Failed to get user by token: {str(e)}", exc_info=True)
            raise

    async def update_user_status(
        self, user_id: int, verified: bool | None = None, banned: bool | None = None
    ) -> None:
        try:
            updates = []
            params = []
            if verified is not None:
                updates.append("verified = ?")
                params.append(int(verified))
            if banned is not None:
                updates.append("banned = ?")
                params.append(int(banned))

            if not updates:
                logger.info(f"No status updates provided for user {user_id}")
                return

            query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
            params.append(user_id)
            await self.conn.execute(query, tuple(params))
            await self.conn.commit()
            logger.info(f"User status updated successfully for user ID: {user_id}")
        except Exception as e:
            logger.error(f"Failed to update user status for user {user_id}: {str(e)}", exc_info=True)
            raise

    # aiosqlite is expecting a tuple, but is recieving an int
    async def delete_user_by_id(self, user_id: int):
        try:
            await self.conn.execute("DELETE FROM users where user_id = ?", (user_id,))
            await self.conn.commit()
            logger.info(f"User deleted successfully: {user_id}")
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {str(e)}", exc_info=True)
            raise

    # Picture functions

    async def add_picture(self, expires: datetime, filepath: str, mimetype: str) -> int | None:
        try:
            query = """
                INSERT INTO pictures (expires, filepath, mimetype)
                VALUES (?, ?, ?)
            """
            cursor = await self.conn.execute(query, (expires, filepath, mimetype))
            await self.conn.commit()
            picture_id = cursor.lastrowid
            logger.info(f"Picture added successfully with ID: {picture_id}")
            return picture_id
        except Exception as e:
            logger.error(f"Failed to add picture: {str(e)}", exc_info=True)
            raise

    async def get_picture(self, picture_id: int) -> PictureMetadata | None:
        try:
            query = "SELECT * FROM pictures WHERE picture_id = ?"
            async with self.conn.execute(query, (picture_id,)) as cursor:
                row = await cursor.fetchone()

            if row:
                picture = PictureMetadata(
                    picture_id=row["picture_id"],
                    expires=row["expires"],
                    filepath=row["filepath"],
                    mimetype=row["mimetype"],
                )
                logger.debug(f"Picture retrieved successfully: {picture_id}")
                return picture
            logger.info(f"No picture found with ID: {picture_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to get picture {picture_id}: {str(e)}", exc_info=True)
            raise

    async def delete_expired_pictures(self) -> list[str]:
        try:
            now = datetime.now(tz=UTC)
            select_query = "SELECT filepath FROM pictures WHERE expires < ?"
            async with self.conn.execute(select_query, (now,)) as cursor:
                rows = await cursor.fetchall()
                filepaths_to_delete = [row["filepath"] for row in rows]

            if filepaths_to_delete:
                delete_query = "DELETE FROM pictures WHERE expires < ?"
                await self.conn.execute(delete_query, (now,))
                await self.conn.commit()
                logger.info(f"Deleted {len(filepaths_to_delete)} expired pictures")

            return filepaths_to_delete
        except Exception as e:
            logger.error(f"Failed to delete expired pictures: {str(e)}", exc_info=True)
            raise

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
        try:
            query = """
                    INSERT INTO foodshares
                    (name, location, ends, active, user_fk_id, picture_fk_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """
            cursor = await self.conn.execute(
                query,
                (name, location, ends, int(active), user_fk_id, picture_fk_id),
            )
            await self.conn.commit()
            foodshare_id = cursor.lastrowid
            logger.info(f"Foodshare added successfully with ID: {foodshare_id}")
            return foodshare_id
        except Exception as e:
            logger.error(f"Failed to add foodshare: {str(e)}", exc_info=True)
            raise

    async def link_foodshare_restriction(self, foodshare_id: int, restriction_id: int) -> None:
        query = """
        INSERT OR IGNORE INTO foodshare_restrictions
        (foodshare_id, restriction_id) VALUES (?, ?)
        """
        await self.conn.execute(query, (foodshare_id, restriction_id))
        await self.conn.commit()

    async def get_foodshare(self, foodshare_id: int) -> Foodshare | None:
        try:
            query = "SELECT * FROM foodshares WHERE foodshare_id = ?"
            async with self.conn.execute(query, (foodshare_id,)) as cursor:
                fs_row = await cursor.fetchone()

            if not fs_row:
                logger.info(f"No foodshare found with ID: {foodshare_id}")
                return None
            if fs_row["user_fk_id"]:
                creator = await self.get_user(fs_row["user_fk_id"])
            else:
                creator = None
            if fs_row["picture_fk_id"]:
                picture = await self.get_picture(fs_row["picture_fk_id"])
            else:
                picture = None

            restrictions_query = """
                SELECT r.label
                FROM restrictions r
                JOIN foodshare_restrictions fr ON r.restriction_id = fr.restriction_id
                WHERE fr.foodshare_id = ?
            """
            async with self.conn.execute(restrictions_query, (foodshare_id,)) as cursor:
                rest_rows = await cursor.fetchall()
                restrictions_list = [row["label"] for row in rest_rows]

            foodshare = Foodshare(
                foodshare_id=fs_row["foodshare_id"],
                name=fs_row["name"],
                location=fs_row["location"],
                ends=fs_row["ends"],
                restrictions=restrictions_list,
                active=bool(fs_row["active"]),
                creator=creator,
                picture=picture,
            )
            logger.debug(f"Foodshare retrieved successfully: {foodshare_id}")
            return foodshare
        except Exception as e:
            logger.error(f"Failed to get foodshare {foodshare_id}: {str(e)}", exc_info=True)
            raise

    async def get_all_active_foodshares(self) -> list[Foodshare]:
        try:
            query = "SELECT foodshare_id FROM foodshares WHERE active = 1"
            async with self.conn.execute(query) as cursor:
                rows = await cursor.fetchall()

            active_foodshares = []
            for row in rows:
                foodshare = await self.get_foodshare(row["foodshare_id"])
                if foodshare:
                    active_foodshares.append(foodshare)

            logger.debug(f"Retrieved {len(active_foodshares)} active foodshares")
            return active_foodshares
        except Exception as e:
            logger.error(f"Failed to get all active foodshares: {str(e)}", exc_info=True)
            raise

    # Survey CRUD

    async def add_survey(
        self,
        num_participants: int,
        experience: int,
        other_thoughts: str,
        foodshare_fk_id: int | None = None,
    ) -> int | None:
        """Inserts a new survey record."""
        try:
            query = """
                    INSERT INTO surveys
                    (num_participants, experience, other_thoughts, foodshare_fk_id)
                    VALUES (?, ?, ?, ?)
                """
            cursor = await self.conn.execute(
                query, (num_participants, experience, other_thoughts, foodshare_fk_id)
            )
            await self.conn.commit()
            survey_id = cursor.lastrowid
            logger.info(f"Survey added successfully with ID: {survey_id}")
            return survey_id
        except Exception as e:
            logger.error(f"Failed to add survey: {str(e)}", exc_info=True)
            raise

    async def get_survey(self, survey_id: int) -> Survey | None:
        try:
            query = "SELECT * FROM surveys WHERE survey_id = ?"
            async with self.conn.execute(query, (survey_id,)) as cursor:
                row = await cursor.fetchone()

            if row:
                foodshare = (
                    await self.get_foodshare(row["foodshare_fk_id"])
                    if row["foodshare_fk_id"]
                    else None
                )
                survey = Survey(
                    survey_id=row["survey_id"],
                    num_participants=row["num_participants"],
                    experience=row["experience"],
                    other_thoughts=row["other_thoughts"],
                    foodshare=foodshare,
                )
                logger.debug(f"Survey retrieved successfully: {survey_id}")
                return survey
            logger.info(f"No survey found with ID: {survey_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to get survey {survey_id}: {str(e)}", exc_info=True)
            raise

    async def get_all_surveys(self) -> list["Survey"]:
        try:
            query = "SELECT survey_id FROM surveys"
            async with self.conn.execute(query) as cursor:
                rows = await cursor.fetchall()

            surveys = []
            for row in rows:
                survey = await self.get_survey(row["survey_id"])
                if survey:
                    surveys.append(survey)
            logger.debug(f"Retrieved {len(surveys)} surveys")
            return surveys
        except Exception as e:
            logger.error(f"Failed to get all surveys: {str(e)}", exc_info=True)
            raise

    async def reset_token_lifetime(self, token_hash: str):
        try:
            await self.conn.execute(
                """UPDATE device_tokens SET last_used = CURRENT_TIMESTAMP
                WHERE token_hash = ?""",
                (token_hash,),
            )
            await self.conn.commit()
            logger.info("Token lifetime reset successfully")
        except Exception as e:
            logger.error(f"Failed to reset token lifetime: {str(e)}", exc_info=True)
            raise

    async def save_otp(self, otp_record: OTPRecord) -> int | None:
        try:
            cursor = await self.conn.execute(
                """
                INSERT INTO otp_codes (email, otp, expires_at)
                VALUES (?, ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    otp = excluded.otp,
                    expires_at = excluded.expires_at
            """,
                (otp_record.email, otp_record.otp, otp_record.expires_at),
            )
            await self.conn.commit()
            logger.info(f"OTP saved successfully for email: {otp_record.email}")
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to save OTP for email {otp_record.email}: {str(e)}", exc_info=True)
            raise

    async def get_otp(self, email: str) -> OTPRecord | None:
        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT email, otp, expires_at FROM otp_codes WHERE email = ?", (email,)
                )
                row = await cursor.fetchone()
                if row:
                    row_dict = dict(row)
                    # Convert string to datetime object
                    row_dict["expires_at"] = datetime.fromisoformat(row_dict["expires_at"])
                    otp_record = OTPRecord(**row_dict)
                else:
                    otp_record = None
                if otp_record:
                    logger.debug(f"OTP retrieved successfully for email: {email}")
                else:
                    logger.info(f"No OTP found for email: {email}")
                return otp_record
        except Exception as e:
            logger.error(f"Failed to get OTP for email {email}: {str(e)}", exc_info=True)
            raise

    async def delete_otp(self, email: str) -> int | None:
        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute("DELETE FROM otp_codes WHERE email = ?", (email,))
                await self.conn.commit()
                logger.info(f"OTP deleted successfully for email: {email}")
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to delete OTP for email {email}: {str(e)}", exc_info=True)
            raise

    async def create_device_token(self, user_id: int, token_hash: str):
        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO device_tokens (token_hash, user_id) VALUES (?, ?)",
                    (token_hash, user_id),
                )
                await self.conn.commit()
                logger.info(f"Device token created successfully for user ID: {user_id}")
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to create device token for user {user_id}: {str(e)}", exc_info=True)
            raise

    async def get_session_by_token(self, token_hash: str) -> DeviceSession | None:
        """Returns a DeviceSession dataclass to validate the auth token."""
        try:
            async with self.conn.cursor() as cursor:
                query = """
                    SELECT d.user_id, u.banned
                    FROM device_tokens d
                    JOIN users u ON d.user_id = u.user_id
                    WHERE d.token_hash = ?
                """
                await cursor.execute(query, (token_hash,))
                row = await cursor.fetchone()
                session = DeviceSession(**dict(row)) if row else None
                if session:
                    logger.debug("Device session retrieved successfully")
                else:
                    logger.info("No device session found with provided token")
                return session
        except Exception as e:
            logger.error(f"Failed to get session by token: {str(e)}", exc_info=True)
            raise

    async def update_token_usage(self, token_hash: str) -> int | None:
        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute(
                    """
                    UPDATE device_tokens
                    SET last_used = CURRENT_TIMESTAMP WHERE token_hash = ?
                    """,
                    (token_hash,),
                )
                await self.conn.commit()
                logger.info("Token usage updated successfully")
        except Exception as e:
            logger.error(f"Failed to update token usage: {str(e)}", exc_info=True)
            raise

    async def create_or_verify_user(self, email: str) -> int | None:
        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute("SELECT user_id FROM users WHERE email = ?", (email,))
                row = await cursor.fetchone()

                if row:
                    await cursor.execute("UPDATE users SET verified = 1 WHERE email = ?", (email,))
                    user_id = row["user_id"]
                    logger.info(f"User verified successfully: {email}")
                else:
                    await cursor.execute(
                        "INSERT INTO users (email, verified, banned) VALUES (?, 1, 0)",
                        (email,),
                    )
                    user_id = cursor.lastrowid
                    logger.info(f"New user created successfully: {email}")

                await self.conn.commit()
                return user_id
        except Exception as e:
            logger.error(f"Failed to create or verify user {email}: {str(e)}", exc_info=True)
            raise
