from dataclasses import dataclass
import datetime

@dataclass
class User:
    user_id: int
    email: str
    verified: bool
    banned: bool

@dataclass
class Foodshare:
    foodshare_id: int
    creator: int
    location: str
    picture_id: int
    end_date: datetime.datetime
    active: bool

@dataclass
class Picture:
    picture_id: int
    expires: datetime.datetime
    image_data: str

@dataclass
class Survey:
    survey_id: int
    foodshare_id: int
    participants: int
    experience: int
    other_thoughts: str

class DatabaseManager:
    def __init__(self, database_path: str) -> None:
        