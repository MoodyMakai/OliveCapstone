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
        """Initialize the LocalFileStorage with a specified upload folder."""
        self.upload_folder = upload_folder
        try:
            os.makedirs(self.upload_folder, exist_ok=True)
        except OSError as e:
            logger.error(f"Initialization error: Failed to create upload folder at {self.upload_folder}. Error: {e}")
            raise

    async def save(self, file_stream: Buffer, extension: str) -> str:
        """Save a file stream to disk with a unique filename."""
        filename = f"{uuid.uuid4()}.{extension}"
        filepath = os.path.join(self.upload_folder, filename)

        try:
            # Using anyio.open_file instead of aiofiles
            async with await anyio.open_file(filepath, "wb") as f:
                await f.write(file_stream)
            return filepath
        except OSError as e:
            logger.error(f"Write error: Failed to save file to {filepath}. Error: {e}")
            raise

    async def delete(self, filepath: str) -> bool:
        """Delete a file from disk."""
        try:
            path = Path(filepath)
            if await path.exists():
                await path.unlink()
            return True
        except OSError as e:
            logger.error(f"Disk error: Failed during deletion of {filepath}. Error: {e}")
            return False
