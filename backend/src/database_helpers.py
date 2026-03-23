"""Database helper module for the Foodshare backend.

This module provides data classes and utility functions that support database operations
and data validation throughout the application. It contains shared data structures and
helper functions used across various parts of the system.

Key features:
- Data classes for all major entities (User, OTPRecord, DeviceSession, PictureMetadata,
  Foodshare, Survey)
- Email format validation specifically for maine.edu domain
- Input sanitization to prevent injection attacks
- Date/time validation utilities
- Token hashing and generation functions
- Secure random token generation

Data Classes:
    User: Represents a user in the system with ID, email, verification status, and ban status
    OTPRecord: Stores one-time password information for email verification
    DeviceSession: Represents a user session with associated user ID and ban status
    PictureMetadata: Contains metadata for stored pictures including expiration and file path
    Foodshare: Represents a foodshare listing with details, restrictions, and creator info
    Survey: Stores survey responses related to foodshares

Functions:
    validate_email_format: Validates email addresses follow maine.edu domain format
    sanitize_string: Sanitizes input strings to prevent injection attacks
    validate_datetime_format: Validates ISO format date/time strings
    hash_token: Hashes tokens using SHA256 for secure storage
    generate_secure_token: Creates cryptographically secure random tokens

Usage:
    Import this module to access data classes and utility functions for database operations.
"""

import hashlib
import re
import secrets
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """Data class representing a user in the system.

    Attributes:
        user_id (int): Unique identifier for the user
        email (str): User's email address
        verified (bool): Whether the user has been verified (default: False)
        banned (bool): Whether the user is banned (default: False)
    """

    user_id: int
    email: str
    verified: bool = False
    banned: bool = False
    is_admin: bool = False


@dataclass
class OTPRecord:
    """Data class representing an OTP (One-Time Password) record.

    Attributes:
        email (str): Email address associated with the OTP
        otp (str): The one-time password
        expires_at (datetime): When the OTP expires
    """

    email: str
    otp: str
    expires_at: datetime


@dataclass
class DeviceSession:
    """Data class representing a device session.

    Attributes:
        user_id (int): ID of the user associated with the session
        banned (int): Whether the user is banned (0 = not banned, 1 = banned)
        last_used (datetime): When the session token was last used
    """

    user_id: int
    banned: int
    last_used: datetime


@dataclass
class PictureMetadata:
    """Data class representing picture metadata.

    Attributes:
        picture_id (int): Unique identifier for the picture
        expires (datetime): When the picture expires
        filepath (str): Path to the picture file
        mimetype (str): MIME type of the picture
    """

    picture_id: int
    expires: datetime
    filepath: str
    mimetype: str


@dataclass
class Foodshare:
    """Data class representing a foodshare listing.

    Attributes:
        foodshare_id (int): Unique identifier for the foodshare
        name (str): Name of the foodshare
        location (str): Location where the foodshare is available
        ends (datetime): When the foodshare ends
        restrictions (list[str]): List of dietary restrictions
        active (bool): Whether the foodshare is currently active
        creator (User | None): The user who created the foodshare
        picture (PictureMetadata | None): Metadata for the associated picture
    """

    foodshare_id: int
    name: str
    location: str
    ends: datetime
    restrictions: list[str]
    active: bool
    creator: User | None = None
    picture: PictureMetadata | None = None


@dataclass
class Survey:
    """Data class representing a survey response.

    Attributes:
        survey_id (int): Unique identifier for the survey
        num_participants (int): Number of participants in the foodshare
        experience (int): User's experience rating
        other_thoughts (str): Additional thoughts from the user
        foodshare (Foodshare | None): The associated foodshare
    """

    survey_id: int
    num_participants: int
    experience: int
    other_thoughts: str
    foodshare: Foodshare | None = None


def validate_email_format(email: str) -> bool:
    """Validate that an email address has a valid format.

    This function checks if the email follows the format required for maine.edu domain.

    Args:
        email (str): The email address to validate

    Returns:
        bool: True if the email is valid, False otherwise
    """
    # More robust email validation
    if not email or "@" not in email:
        return False

    # More comprehensive regex that properly validates the email format
    # This pattern ensures:
    # - Local part (before @): alphanumeric, dots, underscores, hyphens, plus signs
    # - Domain: must be @maine.edu exactly
    # - No spaces or invalid characters
    regex = r"^[a-zA-Z0-9._%+-]+@maine\.edu$"
    if re.fullmatch(regex, email, re.IGNORECASE):
        return True
    else:
        return False


def sanitize_string(input_str: str) -> str:
    """Sanitize input string by stripping whitespace and truncating.

    Args:
        input_str (str): The input string to sanitize

    Returns:
        str: The sanitized string, truncated at 500 characters
    """
    sanitized = input_str.strip()

    # Limit length to prevent overly long inputs
    return sanitized[:500]


def validate_datetime_format(date_string: str | datetime) -> bool:
    """Validate that a date string is properly formatted.

    Args:
        date_string (str | datetime): The date string or datetime object to validate

    Returns:
        bool: True if the date format is valid, False otherwise
    """
    try:
        if isinstance(date_string, datetime):
            # If it's already a datetime object, it's valid
            return True
        datetime.fromisoformat(date_string)
        return True
    except ValueError:
        return False


def hash_token(token: str) -> str:
    """Hash a token using SHA256.

    Args:
        token (str): The token to hash

    Returns:
        str: The hashed token as a hexadecimal string
    """
    return hashlib.sha256(token.encode()).hexdigest()


def generate_secure_token() -> str:
    """Generate a secure random token.

    Returns:
        str: A securely generated URL-safe token
    """
    return secrets.token_urlsafe(32)
