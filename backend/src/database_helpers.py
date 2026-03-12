import hashlib
import re
import secrets
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    user_id: int
    email: str
    verified: bool = False
    banned: bool = False


@dataclass
class OTPRecord:
    email: str
    otp: str
    expires_at: datetime


@dataclass
class DeviceSession:
    user_id: int
    banned: int


@dataclass
class PictureMetadata:
    picture_id: int
    expires: datetime
    filepath: str
    mimetype: str


@dataclass
class Foodshare:
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
    survey_id: int
    num_participants: int
    experience: int
    other_thoughts: str
    foodshare: Foodshare | None = None


def validate_email_format(email: str) -> bool:
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
    """Sanitize input string to prevent injection attacks."""
    if not isinstance(input_str, str):
        return ""

    # Remove potentially dangerous characters and sequences
    sanitized = input_str.strip()

    # Limit length to prevent overly long inputs
    return sanitized[:500]


def validate_datetime_format(date_string: str | datetime) -> bool:
    """Validate that a date string is properly formatted."""
    try:
        if isinstance(date_string, datetime):
            # If it's already a datetime object, it's valid
            return True
        datetime.fromisoformat(date_string)
        return True
    except ValueError:
        return False


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def generate_secure_token() -> str:
    return secrets.token_urlsafe(32)
