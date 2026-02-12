import datetime
from dataclasses import dataclass

import aiosqlite


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
    def __init__(self, db_conn: aiosqlite.Connection) -> None:
        self.db: aiosqlite.Connection = db_conn

    async def init_tables(self):
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, email TEXT NOT NULL, verified INTEGER, banned INTEGER)"
        )
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS foodshares (foodshare_id INTEGER PRIMARY KEY, location TEXT, picture_fk_id INTEGER REFERENCES pictures(picture_id), end_date TEXT NOT NULL, active INTEGER)"
        )
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS pictures (picture_id INTEGER PRIMARY KEY, expires TEXT NOT NULL, data BLOB NOT NULL)"
        )
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS surveys (survey_id INTEGER PRIMARY KEY, foodshare_fk_id REFERENCES foodshares(foodshare_id), num_participants INTEGER, experience INTEGER, other_thoughts TEXT)"
        )
        await self.db.commit()
