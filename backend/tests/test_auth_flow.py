from datetime import UTC, datetime, timedelta

import pytest

from src.app import app as quart_app

pytestmark = pytest.mark.asyncio


async def test_request_otp_invalid_email(client):
    """Verify that OTP requests for non-maine emails are rejected."""
    response = await client.post("/auth/request-otp", json={"email": "hacker@gmail.com"})
    assert response.status_code == 400
    assert (await response.get_json())["error"] == "Invalid email format"


async def test_full_auth_flow(client, test_app):
    """Verify the end-to-end OTP request, verification, and token usage flow."""
    email = "student@maine.edu"

    # 1. Request OTP
    response = await client.post("/auth/request-otp", json={"email": email})
    assert response.status_code == 200
    assert (await response.get_json())["message"] == "OTP sent successfully"

    # 2. Get OTP from DB (as we can't read the email)

    db = quart_app.storage.db
    otp_record = await db.get_otp(email)
    assert otp_record is not None
    otp_code = otp_record.otp

    # 3. Verify OTP
    response = await client.post("/auth/verify-otp", json={"email": email, "otp": otp_code})
    assert response.status_code == 200
    res_json = await response.get_json()
    assert "token" in res_json
    token = res_json["token"]

    # 4. Use Token on a protected route
    response = await client.get("/foodshares", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


async def test_verify_otp_wrong_code(client):
    """Verify that a wrong OTP code results in a 401 error."""
    email = "wrong_otp_test_unique@maine.edu"
    await client.post("/auth/request-otp", json={"email": email})

    response = await client.post("/auth/verify-otp", json={"email": email, "otp": "000000"})
    assert response.status_code == 401
    assert (await response.get_json())["error"] == "Invalid email or OTP"


async def test_verify_otp_expired(client):
    """Verify that an expired OTP code results in a 401 error."""
    # Use highly unique email to avoid 429 from other tests
    import secrets

    email = f"expired_otp_{secrets.token_hex(4)}@maine.edu"
    resp = await client.post("/auth/request-otp", json={"email": email})
    assert resp.status_code == 200

    # Backdate the OTP expiration

    db = quart_app.storage.db
    expired_time = (datetime.now(UTC) - timedelta(minutes=1)).isoformat()
    await db.conn.execute("UPDATE otp_codes SET expires_at = ? WHERE email = ?", (expired_time, email))
    await db.conn.commit()

    # Get the code (even if expired)
    otp_record = await db.get_otp(email)
    if otp_record is None:
        print(f"DEBUG: OTP not found in DB for {email} after request-otp!")
    assert otp_record is not None
    otp_code = otp_record.otp

    response = await client.post("/auth/verify-otp", json={"email": email, "otp": otp_code})
    assert response.status_code == 401
    assert (await response.get_json())["error"] == "OTP has expired"
