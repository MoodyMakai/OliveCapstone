-- Table creation queries for the database initialization

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    verified INTEGER DEFAULT 0,
    banned INTEGER DEFAULT 0,
    is_admin INTEGER DEFAULT 0
);

-- Device tokens table
CREATE TABLE IF NOT EXISTS device_tokens (
    token_hash TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Pictures table
CREATE TABLE IF NOT EXISTS pictures (
    picture_id INTEGER PRIMARY KEY,
    expires TIMESTAMP NOT NULL,
    filepath TEXT NOT NULL,
    mimetype TEXT NOT NULL
);

-- Foodshares table
CREATE TABLE IF NOT EXISTS foodshares (
    foodshare_id INTEGER PRIMARY KEY,
    name TEXT,
    location TEXT,
    ends TIMESTAMP NOT NULL,
    active INTEGER DEFAULT 1 CHECK(active IN (0, 1)),
    user_fk_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    picture_fk_id INTEGER REFERENCES pictures(picture_id) ON DELETE SET NULL
);

-- Restrictions table
CREATE TABLE IF NOT EXISTS restrictions (
    restriction_id INTEGER PRIMARY KEY,
    label TEXT NOT NULL UNIQUE
);

-- Foodshare restrictions junction table
CREATE TABLE IF NOT EXISTS foodshare_restrictions (
    foodshare_id INTEGER,
    restriction_id INTEGER,
    FOREIGN KEY(foodshare_id) REFERENCES foodshares(foodshare_id) ON DELETE CASCADE,
    FOREIGN KEY(restriction_id) REFERENCES restrictions(restriction_id) ON DELETE CASCADE,
    PRIMARY KEY (foodshare_id, restriction_id)
);

-- Surveys table
CREATE TABLE IF NOT EXISTS surveys (
    survey_id INTEGER PRIMARY KEY,
    num_participants INTEGER DEFAULT 0,
    experience INTEGER DEFAULT 0,
    other_thoughts TEXT,
    foodshare_fk_id INTEGER REFERENCES foodshares(foodshare_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS otp_codes (
    email TEXT PRIMARY KEY,
    otp TEXT NOT NULL,
    expires_at DATETIME NOT NULL
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_foodshares_user_fk ON foodshares(user_fk_id);
CREATE INDEX IF NOT EXISTS idx_foodshares_active ON foodshares(active);
CREATE INDEX IF NOT EXISTS idx_foodshares_ends ON foodshares(ends);
CREATE INDEX IF NOT EXISTS idx_pictures_expires ON pictures(expires);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_device_tokens_user_id ON device_tokens(user_id);
