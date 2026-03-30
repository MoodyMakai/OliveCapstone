import pytest

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio


async def test_protected_route_without_auth(client):
    """Verify that a protected route returns 401 when accessed without authorization."""
    response = await client.get("/foodshares")
    assert response.status_code == 401


async def test_protected_route_with_auth(authenticated_client):
    """Verify that a protected route returns 200 when accessed with a valid token."""
    response = await authenticated_client.get("/foodshares")
    assert response.status_code == 200


async def test_admin_route_as_regular_user(authenticated_client):
    """Verify that an admin route returns 403 when accessed by a regular authenticated user."""
    # /surveys GET is protected by @require_admin
    response = await authenticated_client.get("/surveys")
    assert response.status_code == 403


async def test_admin_route_as_admin(admin_client):
    """Verify that an admin route returns 200 when accessed by an admin user."""
    response = await admin_client.get("/surveys")
    assert response.status_code == 200


async def test_expired_token(authenticated_client):
    """Verify that an expired token returns 401."""
    from datetime import datetime, timedelta

    from src.app import app as quart_app

    # Manually backdate the last_used timestamp for the current session
    raw_token = authenticated_client.token
    from src.database_helpers import hash_token

    token_hash = hash_token(raw_token)

    # Update last_used to be 31 days ago
    expired_time = (datetime.now() - timedelta(days=31)).isoformat()
    db = quart_app.storage.db
    await db.conn.execute("UPDATE device_tokens SET last_used = ? WHERE token_hash = ?", (expired_time, token_hash))
    await db.conn.commit()

    response = await authenticated_client.get("/foodshares")
    assert response.status_code == 401
    assert (await response.get_json())["error"] == "Session expired. Please log in again."
