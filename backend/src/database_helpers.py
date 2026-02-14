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
    location: str
    end_date: str
    active: bool
    user: User | None = None
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


def unpack_user_from_row(row: dict) -> User | None:
    if row is None:
        return None
    user_id = row.get("user_id")
    email = row.get("email")
    verified = row.get("verified")
    banned = row.get("banned")
    if user_id is None or email is None or verified is None or banned is None:
        return None
    return User(
        user_id=int(user_id),
        email=str(email),
        verified=bool(verified),
        banned=bool(banned),
    )


def unpack_picture_from_row(row: dict) -> PictureMetadata | None:
    if row is None:
        return None
    picture_id = row.get("picture_id")
    expires = row.get("expires")
    filepath = row.get("filepath")
    mimetype = row.get("mimetype")
    if picture_id is None or expires is None or filepath is None or mimetype is None:
        return None
    return PictureMetadata(
        picture_id=int(picture_id),
        expires=datetime.fromisoformat(expires),
        filepath=str(filepath),
        mimetype=str(mimetype),
    )
