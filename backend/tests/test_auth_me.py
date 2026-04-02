import pytest
from src.app import app as quart_app

pytestmark = pytest.mark.asyncio


async def test_verify_otp_returns_user_data(client, test_app):
    """Verify that /auth/verify-otp returns user information along with the token."""
    email = "user_data_test@maine.edu"

    # 1. Request OTP
    await client.post("/auth/request-otp", json={"email": email})

    # 2. Get OTP from DB
    db = quart_app.storage.db
    otp_record = await db.get_otp(email)
    otp_code = otp_record.otp

    # 3. Verify OTP
    response = await client.post("/auth/verify-otp", json={"email": email, "otp": otp_code})
    assert response.status_code == 200
    res_json = await response.get_json()

    assert "token" in res_json
    assert "user" in res_json
    assert res_json["user"]["email"] == email
    assert "user_id" in res_json["user"]
    assert "is_admin" in res_json["user"]


async def test_auth_me_endpoint(client, test_app):
    """Verify that /auth/me returns the profile of the currently authenticated user."""
    email = "me_endpoint_test@maine.edu"

    # 1. Login to get a token
    await client.post("/auth/request-otp", json={"email": email})
    db = quart_app.storage.db
    otp_record = await db.get_otp(email)
    otp_code = otp_record.otp

    response = await client.post("/auth/verify-otp", json={"email": email, "otp": otp_code})
    token = (await response.get_json())["token"]

    # 2. Call /auth/me
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    res_json = await response.get_json()

    assert res_json["email"] == email
    assert "user_id" in res_json
    assert "is_admin" in res_json


async def test_auth_me_unauthorized(client):
    """Verify that /auth/me requires authentication."""
    response = await client.get("/auth/me")
    assert response.status_code == 401
