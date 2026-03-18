"""Storage service module for the Foodshare backend.

This module provides the StorageService class which handles all storage-related operations
including file management, user registration, foodshare creation with pictures, and survey submissions.
It acts as a bridge between the database layer and the storage layer, coordinating complex operations
that involve both persistent storage and file system operations.

Key features:
- Picture upload and management with automatic cleanup of expired files
- User registration with email validation
- Foodshare creation with associated picture handling
- Survey submission and retrieval
- Database and file system coordination
- Error handling and resource cleanup
- Input sanitization and validation

Classes:
    StorageService: Main service class for coordinating storage operations

Methods:
    __init__: Initialize the service with database and storage managers
    close: Close the database connection
    add_picture_with_file: Save a picture file and record its metadata
    cleanup_expired_pictures: Delete expired picture files from storage and database
    create_foodshare_with_picture: Create foodshare with associated picture
    register_user: Register a new user in the system
    get_user: Retrieve user by ID, email, or token
    verify_user: Mark a user as verified
    list_active_foodshares: Retrieve all active foodshares
    delete_foodshare: Delete foodshare and its associated picture
    submit_survey: Submit a survey response
    list_all_surveys: Retrieve all survey responses
"""

import logging
from collections.abc import Buffer
from datetime import datetime

from src.database import DatabaseManager
from src.database_helpers import (
    User,
    sanitize_string,
    validate_datetime_format,
    validate_email_format,
)
from src.storage import LocalFileStorage

logger = logging.getLogger(__name__)


class StorageService:
    """Service class for managing storage operations including pictures and foodshares.

    This class provides methods to handle file storage, user registration,
    foodshare creation with associated pictures, and survey submissions.
    """

    def __init__(self, db: DatabaseManager, storage: LocalFileStorage) -> None:
        """Initialize the StorageService.

        Args:
            db (DatabaseManager): Database manager instance for database operations
            storage (LocalFileStorage): Storage instance for file operations
        """
        self.db = db
        self.storage = storage

    async def close(self) -> None:
        """Close the database connection.

        This method closes the database connection to free up resources.
        """
        await self.db.close()

    async def add_picture_with_file(
        self,
        file_stream: Buffer,
        extension: str,
        mimetype: str,
        expires: datetime,
    ) -> int | None:
        """Save a picture file and record its metadata in the database.

        Args:
            file_stream (Buffer): The file stream containing the picture data
            extension (str): The file extension of the picture
            mimetype (str): The MIME type of the picture
            expires (datetime): The expiration date/time for the picture

        Returns:
            int | None: The ID of the created picture record, or None if failed
        """
        filepath = None
        try:
            filepath = await self.storage.save(file_stream, extension)

            picture_id = await self.db.add_picture(expires=expires, filepath=filepath, mimetype=mimetype)
            return picture_id

        except Exception as e:
            # Log the error with full traceback for debugging
            logger.error(f"Error saving picture: {e}", exc_info=True)
            if filepath:
                await self.storage.delete(filepath)
            return None

    async def cleanup_expired_pictures(self) -> int:
        """Delete expired picture files from storage and database.

        This method removes all expired pictures from both the filesystem and database.
        It returns the count of successfully deleted files.

        Returns:
            int: The number of expired pictures successfully deleted
        """
        deleted_count = 0

        filepaths_to_delete = await self.db.delete_expired_pictures()

        for filepath in filepaths_to_delete:
            success = await self.storage.delete(filepath)
            if success:
                deleted_count += 1
            else:
                logger.warning(f"Failed to delete physical file: {filepath}")

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
        restrictions: list[str] | None = None,
    ) -> int | None:
        """Create a new foodshare with an associated picture and optional restrictions.

        This method creates a new foodshare entry in the database, including
        uploading and associating a picture with it, and linking any provided
        dietary restrictions.

        Args:
            name (str): The name of the foodshare
            location (str): The location where the foodshare is available
            ends (datetime): When the foodshare ends
            active (bool): Whether the foodshare is currently active
            user_id (int): The ID of the user creating the foodshare
            file_stream: The file stream containing the picture data
            extension (str): The file extension of the picture
            mimetype (str): The MIME type of the picture
            picture_expires (datetime): The expiration date/time for the picture
            restrictions (list[str] | None): A list of restriction labels (e.g., ['Vegan', 'Nut-Free'])

        Returns:
            int | None: The ID of the created foodshare, or None if failed
        """
        # Validate inputs
        if not name or not location:
            return None

        # Sanitize inputs
        name = sanitize_string(name)
        location = sanitize_string(location)

        # Validate date formats
        if not validate_datetime_format(ends):
            return None

        if not validate_datetime_format(picture_expires):
            return None

        picture_id = await self.add_picture_with_file(file_stream, extension, mimetype, picture_expires)

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

        # If foodshare was successfully created, link any provided restrictions
        if foodshare_id and restrictions:
            for restriction in restrictions:
                await self.db.add_restriction_to_foodshare_by_name(foodshare_id, restriction)

        return foodshare_id

    async def register_user(self, email: str) -> int | None:
        """Register a new user in the system.

        Args:
            email (str): The email address of the user to register

        Returns:
            int | None: The ID of the created user, or None if failed
        """
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
        """Retrieve a user from the database by ID, email, or token.

        Args:
            user_id (int | None): The ID of the user to retrieve
            email (str | None): The email address of the user to retrieve
            token (str | None): The authentication token of the user to retrieve

        Returns:
            User | None: The retrieved user object, or None if not found
        """
        if user_id:
            return await self.db.get_user(user_id)
        elif email:
            return await self.db.get_user_by_email(email)
        elif token:
            return await self.db.get_user_by_token(token)
        return None

    async def verify_user(self, user_id: int) -> None:
        """Verify a user's account.

        Args:
            user_id (int): The ID of the user to verify
        """
        await self.db.update_user_status(user_id, True)

    async def delete_foodshare(self, foodshare_id: int) -> bool:
        """Delete a foodshare and its associated picture.

        Args:
            foodshare_id (int): The ID of the foodshare to delete

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        foodshare = await self.db.get_foodshare(foodshare_id)
        if not foodshare:
            return False

        # Handle file and picture record deletion
        if foodshare.picture:
            # Delete physical file
            await self.storage.delete(foodshare.picture.filepath)
            # Delete database record
            await self.db.delete_picture(foodshare.picture.picture_id)

        # Handle foodshare dependencies (restrictions)
        await self.db.delete_foodshare_restrictions(foodshare_id)

        # Handle the foodshare record itself
        await self.db.delete_foodshare_record(foodshare_id)

        return True
