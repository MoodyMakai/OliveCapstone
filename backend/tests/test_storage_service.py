import io
from datetime import UTC, datetime, timedelta

import aiofiles
import anyio
import pytest
from PIL import Image

from src.service import StorageService


@pytest.mark.asyncio
async def test_user_registration(storage_service: StorageService):
    email = "test@maine.edu"
    user_id = await storage_service.register_user(email)
    assert user_id

    user = await storage_service.get_user(user_id)
    assert user
    assert not user.verified

    await storage_service.verify_user(user_id)
    updated_user = await storage_service.get_user(user_id)
    assert updated_user
    assert updated_user.verified is True


@pytest.mark.asyncio
async def test_storage_service_saves_file_and_metadata(storage_service: StorageService):
    # Create a small valid PNG image in memory
    img = Image.new("RGB", (100, 100), color="red")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    dummy_file_stream = img_byte_arr.getvalue()

    expires = datetime.now(tz=UTC) + timedelta(days=1)

    picture_id = await storage_service.add_picture_with_file(
        file_stream=dummy_file_stream,
        extension="png",
        mimetype="image/png",
        expires=expires,
    )

    assert picture_id is not None

    import os

    db_picture = await storage_service.db.get_picture(picture_id)
    assert db_picture is not None
    assert db_picture.mimetype == "image/webp"  # Should be converted to webp

    # Resolve the local physical path from URI
    local_path = os.path.join(storage_service.storage.upload_folder, os.path.basename(db_picture.filepath))
    assert anyio.Path(local_path).exists

    async with aiofiles.open(local_path, "rb") as f:
        saved_bytes = await f.read()

    # Verify it is indeed a WebP image by opening it
    with Image.open(io.BytesIO(saved_bytes)) as saved_img:
        assert saved_img.format == "WEBP"
        assert saved_img.size == (800, 800)
