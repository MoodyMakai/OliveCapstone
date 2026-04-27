"""Authentication routes module for the Foodshare backend.

This module handles all authentication-related endpoints including OTP (One-Time Password)
generation and verification, user authentication, and session management. It provides
email-based authentication with token-based session handling.
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import cast

from quart import Blueprint, current_app, g, jsonify, request
from quart_rate_limiter import rate_limit

from src.core import QuartApp
from src.database_helpers import OTPRecord, User, hash_token, validate_email_format


def conditional_rate_limit(limit: int, period: timedelta):
    """Apply rate limit only if TESTING is not True in app config."""

    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            if current_app.config.get("TESTING"):
                return await f(*args, **kwargs)
            return await rate_limit(limit, period)(f)(*args, **kwargs)

        return decorated_function

    return decorator


logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def require_auth(f):
    """Decorator to require authentication for a route."""

    @wraps(f)
    async def decorated_function(*args, **kwargs):
        app = cast(QuartApp, current_app)
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        raw_token = auth_header.split(" ")[1]
        hashed_token = hash_token(raw_token)

        session = await app.storage.db.get_session_by_token(hashed_token)

        if not session:
            return jsonify({"error": "Invalid or expired token"}), 401

        now = datetime.now(tz=timezone.utc).replace(tzinfo=None)
        if now - session.last_used > timedelta(days=30):
            return jsonify({"error": "Session expired. Please log in again."}), 401

        if session.banned:
            return jsonify({"error": "This account is banned."}), 403

        # Update token usage timestamp
        await app.storage.db.update_token_usage(hashed_token)

        user = await app.storage.get_user(user_id=session.user_id)
        if user is None:
            return jsonify({"error": "The user does not exist"}), 401
        g.user = user

        return await f(*args, **kwargs)

    return decorated_function


def require_admin(f):
    """Decorator to require admin privileges for a route.

    Checks if the user attached to Quart's global `g` object has the is_admin flag set to True.
    MUST be stacked under the @require_auth decorator.
    """

    @wraps(f)
    async def decorated_function(*args, **kwargs):
        # Fetch the user from the global object (populated by @require_auth)
        user = getattr(g, "user", None)

        if not user:
            return jsonify({"error": "Authentication required."}), 401

        if not user.is_admin:
            return jsonify({"error": "You do not have permission to access this resource."}), 403

        return await f(*args, **kwargs)

    return decorated_function


@auth_bp.route("/request-otp", methods=["POST"])
@conditional_rate_limit(3, timedelta(minutes=10))
async def request_otp():
    """Request an OTP (One-Time Password) for email verification.

    Validates the email format and sends an OTP if valid.

    Returns:
        tuple: JSON response indicating success or error
    """
    app = cast(QuartApp, current_app)
    data = await request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    # Validate email format
    if not validate_email_format(email):
        return jsonify({"error": "Invalid email format"}), 400

    # Check if user exists and is banned
    user = await app.storage.get_user(email=email)
    if user and user.banned:
        return jsonify({"error": "This account is banned."}), 403

    otp = "".join(str(secrets.randbelow(10)) for _ in range(6))
    expires_at = datetime.now(tz=timezone.utc) + timedelta(minutes=10)

    otp_record = OTPRecord(email=email, otp=otp, expires_at=expires_at)
    await app.storage.db.save_otp(otp_record)

    # Use the injected email service
    app.add_background_task(app.email_service.send_otp, email, otp)

    return jsonify({"message": "OTP sent successfully"}), 200


@auth_bp.route("/verify-otp", methods=["POST"])
@conditional_rate_limit(5, timedelta(minutes=1))
async def verify_otp():
    """Verify the OTP provided by the user.

    Validates the OTP against the stored value and creates a session token
    if successful.

    Returns:
        tuple: JSON response with authentication status and token or error
    """
    app = cast(QuartApp, current_app)
    data = await request.get_json()
    email = data.get("email")
    input_otp = data.get("otp")

    if not email or not input_otp:
        return jsonify({"error": "Email and OTP are required"}), 400

    # Validate email format
    if not validate_email_format(email):
        return jsonify({"error": "Invalid email format"}), 400

    generic_error = "Invalid email or OTP"
    record = await app.storage.db.get_otp(email)
    if not record:
        return jsonify({"error": generic_error}), 401

    expires_at = record.expires_at
    if datetime.now(tz=timezone.utc) > expires_at:
        await app.storage.db.delete_otp(email)
        return jsonify({"error": "OTP has expired"}), 401

    if record.otp != input_otp:
        return jsonify({"error": generic_error}), 401

    await app.storage.db.delete_otp(email)

    user_id = await app.storage.db.create_or_verify_user(email)
    if user_id is None:
        return jsonify({"error": "Internal Server Error"}), 500

    user = await app.storage.get_user(user_id=user_id)
    if user and user.banned:
        return jsonify({"error": "This account is banned."}), 403

    raw_token = secrets.token_urlsafe(32)
    hashed_token = hash_token(raw_token)
    await app.storage.db.create_device_token(user_id, hashed_token)

    if user is None:
        return jsonify({"error": "Failed to retrieve user information"}), 500

    return (
        jsonify(
            {
                "message": "Authentication successful",
                "token": raw_token,
                "user": {
                    "user_id": user.user_id,
                    "email": user.email,
                    "is_admin": user.is_admin,
                },
            }
        ),
        200,
    )


@auth_bp.route("/me", methods=["GET"])
@require_auth
async def get_current_user():
    """Retrieve the profile of the currently authenticated user.

    Returns:
        tuple: JSON response with user details
    """
    user = cast(User, g.user)
    return (
        jsonify(
            {
                "user_id": user.user_id,
                "email": user.email,
                "is_admin": user.is_admin,
            }
        ),
        200,
    )


@auth_bp.route("/logout", methods=["POST"])
@require_auth
async def logout():
    """Logout the current user by deleting their session token.

    Returns:
        tuple: JSON response with success message
    """
    app = cast(QuartApp, current_app)
    auth_header = request.headers.get("Authorization")
    # auth_header is guaranteed to exist and start with "Bearer " by @require_auth
    raw_token = auth_header.split(" ")[1]  # pyright: ignore[reportOptionalMemberAccess]
    hashed_token = hash_token(raw_token)

    await app.storage.db.delete_device_token(hashed_token)

    return jsonify({"message": "Successfully logged out"}), 200
