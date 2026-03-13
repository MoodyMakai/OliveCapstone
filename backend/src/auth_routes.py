"""Authentication routes module for the Foodshare backend.

This module handles all authentication-related endpoints including OTP (One-Time Password)
generation and verification, user authentication, and session management. It provides
email-based authentication with token-based session handling.

The module implements:
- OTP request and verification for email authentication
- User session token generation and validation
- Authentication decorators for protecting routes
- Email sending functionality (stub implementation)
- Banned user account handling

Key features:
- Secure OTP generation and storage with expiration
- Token-based authentication system
- Session management and token usage tracking
- Email format validation
- Authentication decorator for route protection
- Proper error handling and status codes

Endpoints:
    POST /auth/request-otp: Request an OTP for email verification
    POST /auth/verify-otp: Verify the OTP and authenticate user

Usage:
    Import this module to register authentication routes with the main application.

    The require_auth decorator can be applied to any route that requires
    authentication, ensuring only valid users can access protected endpoints.

Attributes:
    app (QuartApp): The main Quart application instance
    logger: Application logger for tracking authentication events and errors

Decorators:
    require_auth: Decorator to protect routes requiring authentication

Functions:
    send_email: Stub function for sending OTP emails (to be implemented in production)
"""

import logging
import secrets
from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import cast

from quart import Blueprint, current_app, g, jsonify, request
from quart_rate_limiter import rate_limit

from src.core import QuartApp
from src.database_helpers import OTPRecord, hash_token, validate_email_format

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


async def send_email(email: str, otp: str):
    """Send an email with the OTP to the specified email address.

    In production, this would send an actual email. For now, it logs
    the OTP for debugging purposes.

    Args:
        email (str): The recipient's email address
        otp (str): The one-time password to send
    """
    print(f"Send {otp} to {email}")


@auth_bp.route("/request-otp", methods=["POST"])
@rate_limit(3, timedelta(minutes=10))
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
    expires_at = datetime.now(tz=UTC) + timedelta(minutes=10)

    otp_record = OTPRecord(email=email, otp=otp, expires_at=expires_at)
    await app.storage.db.save_otp(otp_record)

    app.add_background_task(send_email, email, otp)
    return jsonify({"message": "OTP sent successfully"}), 200


@auth_bp.route("/auth/verify-otp", methods=["POST"])
@rate_limit(5, timedelta(minutes=1))
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
    if datetime.now(tz=UTC) > expires_at:
        await app.storage.db.delete_otp(email)
        return jsonify({"error": "OTP has expired"}), 401

    if record.otp != input_otp:
        return jsonify({"error": generic_error}), 401

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
    """Decorator to require authentication for a route.

    Checks if the user has a valid session token in the Authorization header.

    Args:
        f (function): The function to decorate

    Returns:
        function: The decorated function with authentication check
    """

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
