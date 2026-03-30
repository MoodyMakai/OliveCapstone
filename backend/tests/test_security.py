import secrets

import pytest

from src.app import app as quart_app
from src.database_helpers import hash_token

pytestmark = pytest.mark.asyncio


async def test_manual_user_registration(client):
    """Verify that a user can register via the /users endpoint."""
    email = "newuser@maine.edu"
    response = await client.post("/users", json={"email": email})
    assert response.status_code == 201
    assert (await response.get_json())["user_id"] is not None

    # Check duplicate
    response = await client.post("/users", json={"email": email})
    assert response.status_code == 400
    assert (await response.get_json())["error"] == "A user with that email already exists."


async def test_banned_user_blocked(client):
    """Verify that a banned user is rejected from all protected routes."""
    db = quart_app.storage.db
    email = "banned_security@maine.edu"
    user_id = await db.add_user(email, verified=True, banned=True)
    assert user_id

    raw_token = secrets.token_urlsafe(32)
    token_hash = hash_token(raw_token)
    await db.create_device_token(user_id, token_hash)

    response = await client.get("/foodshares", headers={"Authorization": f"Bearer {raw_token}"})
    assert response.status_code == 403
    assert (await response.get_json())["error"] == "This account is banned."


async def test_rate_limiting_disabled_in_tests(client):
    """Verify that the rate limiter is disabled when TESTING=True."""
    import secrets

    email = f"no_limit_{secrets.token_hex(8)}@maine.edu"

    # We should be able to do more than the limit (3) without 429
    for i in range(5):
        response = await client.post("/auth/request-otp", json={"email": email})
        assert response.status_code == 200
