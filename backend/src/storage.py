import os
import uuid

import aiofiles
from _typeshed import ReadableBuffer
from anyio import Path


class LocalFileStorage:
    def __init__(self, upload_folder: str) -> None:
        self.upload_folder = upload_folder
        os.makedirs(self.upload_folder, exist_ok=True)

    async def save(self, file_stream: ReadableBuffer, extension: str) -> str:
        filename = f"{uuid.uuid4()}.{extension}"
        filepath = os.path.join(self.upload_folder, filename)

        async with aiofiles.open(filepath, "wb") as f:
            await f.write(file_stream)
        return filepath

    async def delete(self, filepath: str) -> bool:
        try:
            path = Path(filepath)
            if await path.exists():
                os.remove(filepath)
            return True
        except OSError as e:
            print(f"Disk error: {e}")
            return False
