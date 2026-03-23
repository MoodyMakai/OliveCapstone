"""Local file storage module for the Foodshare backend.

This module provides the LocalFileStorage class for managing file uploads and deletions
using the local filesystem. It handles saving files with unique filenames and provides
methods for deleting files when needed.
"""

import logging
import os
import uuid
from collections.abc import Buffer

import anyio
from anyio import Path

# Initialize module-level logger
logger = logging.getLogger(__name__)


class LocalFileStorage:
    """Local file storage manager for handling file uploads and deletions."""

    def __init__(self, upload_folder: str) -> None:
        """Initialize the LocalFileStorage with a specified upload folder.

        Args:
            upload_folder (str): The physical directory where files are stored.
        """
        self.upload_folder = upload_folder
        try:
            os.makedirs(self.upload_folder, exist_ok=True)
        except OSError as e:
            logger.error(f"Initialization error: Failed to create upload folder at {self.upload_folder}. Error: {e}")
            raise

    async def save(self, file_stream: Buffer, extension: str) -> str:
        """Save a file stream to disk with a unique filename.

        Returns:
            str: The public URI path for the saved file (e.g., '/images/uuid.png')
        """
        filename = f"{uuid.uuid4()}.{extension}"
        filepath = os.path.join(self.upload_folder, filename)

        try:
            async with await anyio.open_file(filepath, "wb") as f:
                await f.write(file_stream)
            # Return a standardized public URI
            return f"/images/{filename}"
        except OSError as e:
            logger.error(f"Write error: Failed to save file to {filepath}. Error: {e}")
            raise

    async def delete(self, uri: str) -> bool:
        """Delete a file from disk based on its public URI.

        Args:
            uri (str): The public URI of the file (e.g., '/images/uuid.png')

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            # Extract the filename from the URI
            filename = os.path.basename(uri)
            filepath = os.path.join(self.upload_folder, filename)

            path = Path(filepath)
            if await path.exists():
                await path.unlink()
            return True
        except OSError as e:
            logger.error(f"Disk error: Failed during deletion of {uri}. Error: {e}")
            return False
