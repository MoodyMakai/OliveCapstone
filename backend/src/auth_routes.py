import secrets
from datetime import UTC, datetime, timedelta
from functools import wraps

from quart import g, jsonify, request

from src.app import app
from src.database_helpers import OTPRecord, hash_token, validate_email_format


async def send_email(email: str, otp: str):
    # In production, this would send an actual email
    # For now, we'll just log it for debugging purposes
    print(f"Send {otp} to {email}")


@app.route("/auth/request-otp", methods=["POST"])
async def request_otp():
    data = await request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Validate email format
    if not validate_email_format(email):
        return jsonify({"error": "Invalid email format"}), 400

    # TODO: Add rate limiting to prevent abuse
    otp = "".join(str(secrets.randbelow(10)) for _ in range(6))
    # Check if user exists and is banned
    user = await app.storage.get_user(email=email)
    if user and user.banned:
        return jsonify({"error": "This account is banned."}), 403

    otp = "".join(str(secrets.randbelow(10)) for _ in range(6))
    expires_at = datetime.now(tz=UTC) + timedelta(minutes=10)

    otp_record = OTPRecord(email=email, otp=otp, expires_at=expires_at)
    await app.storage.db.save_otp(otp_record)

    await send_email(email, otp)
    return jsonify({"message": "OTP sent successfully"}), 200


@app.route("/auth/verify-otp", methods=["POST"])
async def verify_otp():
    data = await request.get_json()
    email = data.get("email")
    input_otp = data.get("otp")

    if not email or not input_otp:
        return jsonify({"error": "Email and OTP are required"}), 400

    # Validate email format
    if not validate_email_format(email):
        return jsonify({"error": "Invalid email format"}), 400

    record = await app.storage.db.get_otp(email)
    if not record:
        return jsonify({"error": "No OTP found for this email"}), 401

    expires_at = record.expires_at
    if datetime.now(tz=UTC) > expires_at:
        await app.storage.db.delete_otp(email)
        return jsonify({"error": "OTP has expired"}), 401

    if record.otp != input_otp:
        return jsonify({"error": "Invalid OTP"}), 401

    await app.storage.db.delete_otp(email)

    user = await app.storage.get_user(email=email)
    if user and user.banned:
        return jsonify({"error": "This account is banned."}), 403

    user_id = await app.storage.db.create_or_verify_user(email)
    if user_id is None:
        return jsonify({"error": "Internal Server Error"}), 500

    raw_token = secrets.token_urlsafe(32)
    hashed_token = hash_token(raw_token)
    await app.storage.db.create_device_token(user_id, hashed_token)

    return jsonify({"message": "Authentication successful", "token": raw_token}), 200


def require_auth(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        raw_token = auth_header.split(" ")[1]
        hashed_token = hash_token(raw_token)

        session = await app.storage.db.get_session_by_token(hashed_token)

        if not session:
            return jsonify({"error": "Invalid or expired token"}), 401

        if session.banned:
            return jsonify({"error": "This account is banned."}), 403

        # Update token usage timestamp
        await app.storage.db.update_token_usage(hashed_token)
        g.user_id = session.user_id

        return await f(*args, **kwargs)

    return decorated_function
