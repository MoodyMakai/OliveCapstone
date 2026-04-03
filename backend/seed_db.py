import asyncio
import os
import secrets
import sys
from datetime import datetime, timedelta, timezone

# Add the parent directory to sys.path to import from src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import DatabaseManager
from src.database_helpers import hash_token


async def seed():
    db_path = "stress_test.sqlite"
    if os.path.exists(db_path):
        os.remove(db_path)

    db = DatabaseManager(db_path)
    await db.connect()
    await db.init_tables()

    print(f"Seeding database at {db_path}...")

    # Create users
    num_users = 100
    tokens = []
    print(f"Creating {num_users} users...")
    for i in range(num_users):
        email = f"stress_user{i}@maine.edu"
        user_id = await db.add_user(email, verified=True)

        # Create a token for each user
        raw_token = secrets.token_urlsafe(32)
        token_hash = hash_token(raw_token)
        await db.create_device_token(user_id, token_hash)
        tokens.append(raw_token)

    # Save tokens to a file for Locust to use
    with open("test_tokens.txt", "w") as f:
        for token in tokens:
            f.write(f"{token}\n")

    # Create foodshares
    num_foodshares = 50
    print(f"Creating {num_foodshares} foodshares...")
    for i in range(num_foodshares):
        user_id = (i % num_users) + 1
        # Use a real-looking datetime for ends
        ends = datetime.now(timezone.utc) + timedelta(hours=i % 24 + 1)
        await db.add_foodshare(
            name=f"Stress Foodshare {i}", location=f"Stress Location {i}", ends=ends, active=True, user_fk_id=user_id
        )

    await db.close()
    print("Seeding complete. Tokens saved to test_tokens.txt")


if __name__ == "__main__":
    asyncio.run(seed())
