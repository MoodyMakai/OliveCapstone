from datetime import datetime

from _typeshed import ReadableBuffer

from src.database import DatabaseManager
from src.database_helpers import User, validate_email_format
from src.storage import LocalFileStorage


class StorageService:
    def __init__(self, db: DatabaseManager, storage: LocalFileStorage) -> None:
        self.db = db
        self.storage = storage

    async def upload_image(
        self, image_bytes: ReadableBuffer, mimetype: str, expires: datetime
    ) -> int | None:
        ext = mimetype.split("/")[-1]
        filepath = await self.storage.save(image_bytes, ext)
        try:
            picture_id = await self.db.add_picture_metadata(expires, filepath, mimetype)
            return picture_id
        except Exception as e:
            # If the database insert fails, we remove the image from storage
            await self.storage.delete(filepath)
            raise e

    async def delete_image(self, picture_id: int) -> bool:
        picture = await self.db.get_picture_metadata_by_id(picture_id)
        if picture is None:
            return False

        await self.db.delete_picture_metadata(picture_id)

        await self.storage.delete(picture.filepath)
        return True

    async def create_user(self, email: str) -> int | None:
        if not validate_email_format(email):
            return None
        user_id = await self.db.add_user(email)
        return user_id

    async def is_picture_expired(self, picture_id: int) -> bool:
        picture = await self.db.get_picture_metadata_by_id(picture_id)
        if picture is None:
            return False
        return picture.expires > datetime.now()

    async def delete_expired_pictures(self):
        pictures = await self.db.get_expired_pictures()
        for picture in pictures:
            await self.delete_image(picture.picture_id)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.db.get_user_by_email(email)

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.db.get_user_by_id(user_id)
