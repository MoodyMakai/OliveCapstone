import re
from dataclasses import dataclass
from datetime import datetime

import aiosqlite


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


def unpack_user_from_row(row: aiosqlite.Row) -> User:
    user_id = int(row["user_id"])
    email = row["email"]
    verified = bool(row["verified"])
    banned = bool(row["banned"])
    return User(
        user_id=user_id,
        email=email,
        verified=verified,
        banned=banned,
    )


def unpack_picture_from_row(row: aiosqlite.Row) -> PictureMetadata:
    picture_id = int(row["picture_id"])
    expires = datetime.fromisoformat(row["expires"])
    filepath = row["filepath"]
    mimetype = row["mimetype"]
    return PictureMetadata(
        picture_id=picture_id,
        expires=expires,
        filepath=filepath,
        mimetype=mimetype,
    )


def unpack_foodshare_from_row(row: aiosqlite.Row) -> Foodshare | None:
    # unpack user
    user_id = int(row["user_id"])
    email = row["email"]
    verified = bool(row["verified"])
    banned = bool(row["banned"])

    # unpack picture
    picture_id = int(row["picture_id"])
    expires = datetime.fromisoformat(row["datetime"])
    filepath = row["filepath"]
    mimetype = row["mimetype"]

    # unpack foodshare
    foodshare_id = int(row["foodshare_id"])
    name = row["name"]
    location = row["location"]
    ends = datetime.fromisoformat(row["ends"])
    active = bool(row["active"])

    # pack and return Foodshare
    user = User(user_id, email, verified, banned)
    picture_metadata = PictureMetadata(picture_id, expires, filepath, mimetype)
    return Foodshare(foodshare_id, name, location, ends, active, user, picture_metadata)
