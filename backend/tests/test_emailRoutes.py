import pytest

from src.app import app
from src.database import DatabaseManager
from src.tokens import generate_verification_token


# Used to run async tests from pytest
# Responses are in json via jsonify, so in tests use json
@pytest.mark.asyncio
async def test_verify_email_missing_token():
    async with app.test_client() as client:
        # Website Suffix for token. Everything that isn't the domain
        response = await client.get("/verify/verify-email?token=")
        # Error code for this type of resposne
        assert response.status_code == 400
        # Retrieve Json
        json_data = await response.get_json()
        # Must be same as route error
        assert json_data["error"] == "failed to validate, missing token."


@pytest.mark.asyncio
async def test_verify_email_invalid_token():
    evil_token = "token_of_doom_and_despair_only_for_test_purposes"
    async with app.test_client() as client:
        response = await client.get(f"/verify/verify-email?token={evil_token}")
        assert response.status_code == 404
        json_data = await response.get_json()
        assert json_data["error"] == "token has expired or is invalid"


@pytest.mark.asyncio
async def test_verify_email_success():
    email = "test.user@maine.edu"
    valid_token = generate_verification_token(email)
    # Copied from App.py initializes db manager
    # Initalizes connection to db

    async with app.app_context():
        # if the database has been initalized contiune, if not it needs to
        # be or it will fail this test.
        if not hasattr(app, "db"):
            app.db = DatabaseManager(db_path=app.config["DB_PATH"])
        await app.db.connect()
        await app.db.init_tables()
        # Trouble Shooting

        await app.db.add_user(email)
        user_info = await app.db.get_user_by_email(email)
        # User id should be user_id field of user
        if not user_info:
            pytest.fail("User not In database")
        user_Id = user_info.user_id
    # Test
    async with app.test_client() as client:
        response = await client.get(f"/verify/verify-email?token={valid_token}")
        assert response.status_code == 200
        json_data = await response.get_json()
        assert json_data["message"] == "email has been successfully verified"
        await app.db.delete_user_by_id(user_Id)
    # Closes connection at end of test once User has been deleted.

    await app.db.close()

    # If test fails it's most likely due to the failure
    # of deleting the account after a test/ account exists
