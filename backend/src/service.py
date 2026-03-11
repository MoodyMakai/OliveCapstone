from collections.abc import Buffer
from datetime import datetime

from src.database import DatabaseManager
from src.database_helpers import (
    Foodshare,
    Survey,
    User,
    sanitize_string,
    validate_datetime_format,
    validate_email_format,
)
from src.storage import LocalFileStorage


class StorageService:
    def __init__(self, db: DatabaseManager, storage: LocalFileStorage) -> None:
        self.db = db
        self.storage = storage

    async def close(self) -> None:
        await self.db.close()

    async def add_picture_with_file(
        self,
        file_stream: Buffer,
        extension: str,
        mimetype: str,
        expires: datetime,
    ) -> int | None:

        filepath = None
        try:
            filepath = await self.storage.save(file_stream, extension)

            picture_id = await self.db.add_picture(
                expires=expires, filepath=filepath, mimetype=mimetype
            )
            return picture_id

        except Exception as e:
            print(f"Error saving picture: {e}")
            if filepath:
                await self.storage.delete(filepath)
            return None

    async def cleanup_expired_pictures(self) -> int:
        deleted_count = 0

        filepaths_to_delete = await self.db.delete_expired_pictures()

        for filepath in filepaths_to_delete:
            success = await self.storage.delete(filepath)
            if success:
                deleted_count += 1
            else:
                print(f"Failed to delete physical file: {filepath}")

        return deleted_count

    async def create_foodshare_with_picture(
        self,
        name: str,
        location: str,
        ends: datetime,
        active: bool,
        user_id: int,
        file_stream,
        extension: str,
        mimetype: str,
        picture_expires: datetime,
    ) -> int | None:
        # Validate inputs
        if not name or not location:
            return None

        # Sanitize inputs
        name = sanitize_string(name)
        location = sanitize_string(location)

        # Validate date formats
        if not validate_datetime_format(ends.isoformat()):
            return None

        if not validate_datetime_format(picture_expires.isoformat()):
            return None

        picture_id = await self.add_picture_with_file(
            file_stream, extension, mimetype, picture_expires
        )

        if not picture_id:
            return None

        foodshare_id = await self.db.add_foodshare(
            name=name,
            location=location,
            ends=ends,
            active=active,
            user_fk_id=user_id,
            picture_fk_id=picture_id,
        )
        return foodshare_id

    async def register_user(self, email: str) -> int | None:
        # Validate and sanitize email
        if not email:
            return None

        email = sanitize_string(email)
        if not validate_email_format(email):
            return None
        return await self.db.add_user(email, False, False)

    async def get_user(
        self,
        user_id: int | None = None,
        email: str | None = None,
        token: str | None = None,
    ) -> User | None:
        if user_id:
            return await self.db.get_user(user_id)
        elif email:
            return await self.db.get_user_by_email(email)
        elif token:
            return await self.db.get_user_by_token(token)
        return None

    async def verify_user(self, user_id: int) -> None:
        await self.db.update_user_status(user_id, True)

    async def list_active_foodshares(self) -> list[Foodshare]:
        return await self.db.get_all_active_foodshares()

    async def delete_foodshare(self, foodshare_id: int) -> bool:
        foodshare = await self.db.get_foodshare(foodshare_id)
        if not foodshare:
            return False

        if foodshare.picture:
            await self.storage.delete(foodshare.picture.filepath)
            await self.db.conn.execute(
                "DELETE FROM pictures WHERE picture_id = ?",
                (foodshare.picture.picture_id,),
            )

        await self.db.conn.execute(
            "DELETE FROM foodshare_restrictions WHERE foodshare_id = ?", (foodshare_id,)
        )

        await self.db.conn.execute(
            "DELETE FROM foodshares WHERE foodshare_id = ?", (foodshare_id,)
        )
        await self.db.conn.commit()

        return True

    async def submit_survey(
        self,
        num_participants: int,
        experience: int,
        other_thoughts: str,
        foodshare_id: int | None = None,
    ) -> int | None:
        return await self.db.add_survey(
            num_participants=num_participants,
            experience=experience,
            other_thoughts=other_thoughts,
            foodshare_fk_id=foodshare_id,
        )

    async def list_all_surveys(self) -> list[Survey]:
        return await self.db.get_all_surveys()
