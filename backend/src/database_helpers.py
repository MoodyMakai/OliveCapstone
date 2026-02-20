import re
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    user_id: int
    email: str
    verified: bool = False
    banned: bool = False


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
    # Regex explanation:
    # [^@\s]+: Matches one or more characters that aren't '@' or whitespace
    # @maine\.edu: Matches the literal characters: @maine.edu
    regex = r"[^@\s]+@maine\.edu"
    if re.fullmatch(regex, email, re.IGNORECASE):
        return True
    else:
        return False
