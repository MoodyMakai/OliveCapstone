"""Local file storage module for the Foodshare backend.

This module provides the LocalFileStorage class for managing file uploads and deletions
using the local filesystem. It handles saving files with unique filenames and provides
methods for deleting files when needed.

Key features:
- UUID-based filename generation to ensure uniqueness
- Asynchronous file operations using aiofiles
- Automatic directory creation for upload storage
- Error handling for file system operations
- Simple save and delete interface

Classes:
    LocalFileStorage: Manages local file storage operations with unique filename generation

Methods:
    __init__: Initialize the storage manager with upload folder path
    save: Save a file stream to disk with a unique filename
    delete: Delete a file from disk
"""

import os
import uuid
from collections.abc import Buffer

import aiofiles
from anyio import Path


class LocalFileStorage:
    """Local file storage manager for handling file uploads and deletions.

    This class provides methods to save files to disk and delete them when needed,
    using UUID-based filenames to ensure uniqueness.
    """

    def __init__(self, upload_folder: str) -> None:
        """Initialize the LocalFileStorage with a specified upload folder.

        Args:
            upload_folder (str): The path to the folder where files will be stored
        """
        self.upload_folder = upload_folder
        os.makedirs(self.upload_folder, exist_ok=True)

    async def save(self, file_stream: Buffer, extension: str) -> str:
        """Save a file stream to disk with a unique filename.

        Args:
            file_stream (Buffer): The file stream containing the data to save
            extension (str): The file extension to use for the saved file

        Returns:
            str: The full filepath of the saved file
        """
        filename = f"{uuid.uuid4()}.{extension}"
        filepath = os.path.join(self.upload_folder, filename)

        async with aiofiles.open(filepath, "wb") as f:
            await f.write(file_stream)
        return filepath

    async def delete(self, filepath: str) -> bool:
        """Delete a file from disk.

        Args:
            filepath (str): The path to the file to delete

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            path = Path(filepath)
            if await path.exists():
                os.remove(filepath)
            return True
        except OSError as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Disk error: {e}")
            return False
