import io
from datetime import UTC, datetime, timedelta

import pytest
from PIL import Image

from src.app import app as quart_app

pytestmark = pytest.mark.asyncio


async def test_get_foodshares_empty(authenticated_client):
    """Verify that the foodshare list is empty initially."""
    response = await authenticated_client.get("/foodshares")
    assert response.status_code == 200
    assert await response.get_json() == []


async def test_create_foodshare_success(authenticated_client):
    """Verify that a user can create a foodshare with an image."""
    from werkzeug.datastructures import FileStorage

    # Create a dummy image
    img = Image.new("RGB", (100, 100), color="blue")
    img_buf = io.BytesIO()
    img.save(img_buf, format="JPEG")
    img_buf.seek(0)

    form_data = {
        "name": "Free Pizza",
        "location": "Union Hall",
        "ends": (datetime.now() + timedelta(hours=2)).isoformat(),
        "picture_expires": (datetime.now() + timedelta(days=1)).isoformat(),
        "active": "true",
    }
    files = {"picture": FileStorage(img_buf, filename="pizza.jpg", content_type="image/jpeg")}

    # Use the raw client and headers to bypass the wrapper for this complex multipart request
    response = await authenticated_client.client.post(
        "/foodshares", form=form_data, files=files, headers=authenticated_client.headers
    )

    assert response.status_code == 201
    res_json = await response.get_json()
    assert res_json["success"] is True
    assert "foodshare_id" in res_json


async def test_get_foodshares_active_filtering(authenticated_client, admin_client):
    """Verify that only active and non-expired foodshares are returned."""
    # Ensure a fresh state for filtering

    db = quart_app.storage.db

    # Clear existing foodshares
    await db.conn.execute("DELETE FROM foodshares")
    await db.conn.commit()

    # 1. Create an active foodshare
    img = Image.new("RGB", (100, 100), color="green")
    img_buf = io.BytesIO()
    img.save(img_buf, format="JPEG")
    img_buf.seek(0)

    # Use StorageService to create it (handles images)
    await quart_app.storage.create_foodshare_with_picture(
        name="Active Pizza",
        location="Union",
        ends=datetime.now(UTC) + timedelta(hours=2),
        active=True,
        user_id=1,
        file_stream=img_buf.getvalue(),
        extension="jpg",
        mimetype="image/jpeg",
        picture_expires=datetime.now(UTC) + timedelta(days=1),
    )

    # 2. Create an inactive foodshare
    await quart_app.storage.create_foodshare_with_picture(
        name="Inactive Pizza",
        location="Union",
        ends=datetime.now(UTC) + timedelta(hours=2),
        active=False,
        user_id=1,
        file_stream=img_buf.getvalue(),
        extension="jpg",
        mimetype="image/jpeg",
        picture_expires=datetime.now(UTC) + timedelta(days=1),
    )

    # 3. Create an expired foodshare
    await db.conn.execute(
        "INSERT INTO foodshares (name, location, ends, active, user_fk_id) VALUES (?, ?, ?, ?, ?)",
        ("Expired Pizza", "Union", "2000-01-01T00:00:00", 1, 1),
    )
    await db.conn.commit()

    # Check listing
    response = await authenticated_client.get("/foodshares")
    assert response.status_code == 200
    res_json = await response.get_json()

    # Should only contain 'Active Pizza'
    assert len(res_json) == 1
    assert res_json[0]["name"] == "Active Pizza"


async def test_close_foodshare_permissions(authenticated_client, admin_client):
    """Verify that only the creator can close a foodshare."""
    db = quart_app.storage.db

    # Create a foodshare as user 1
    fs_id = await db.add_foodshare(
        name="My Pizza", location="Union", ends=datetime.now() + timedelta(hours=1), active=True, user_fk_id=1
    )
    assert fs_id

    # Try to close as admin (who is user 2)
    response = await admin_client.post("/foodshares/close", json={"foodshare_id": fs_id})
    assert response.status_code == 403
    assert (await response.get_json())["error"] == "You do not have permission to close this foodshare"

    # Close as creator
    response = await authenticated_client.post("/foodshares/close", json={"foodshare_id": fs_id})
    assert response.status_code == 200
    assert (await response.get_json())["success"] is True

    # Verify it is now inactive
    fs = await db.get_foodshare(fs_id)
    assert fs
    assert fs.active is False
