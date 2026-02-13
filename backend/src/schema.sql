CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    verified INTEGER,
    banned INTEGER
);
CREATE TABLE IF NOT EXISTS pictures (
    picture_id INTEGER PRIMARY KEY,
    expires TEXT NOT NULL,
    data BLOB NOT NULL
);
CREATE TABLE IF NOT EXISTS foodshares (
    foodshare_id INTEGER PRIMARY KEY,
    creator_id REFERENCES users(user_id),
    location TEXT,
    picture_fk_id INTEGER REFERENCES pictures(picture_id),
    end_date TEXT NOT NULL,
    active INTEGER
);
CREATE TABLE IF NOT EXISTS surveys (
    survey_id INTEGER PRIMARY KEY,
    foodshare_fk_id REFERENCES foodshares(foodshare_id),
    num_participants INTEGER,
    experience INTEGER,
    other_thoughts TEXT
);
