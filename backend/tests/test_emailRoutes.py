import pytest

from src.app import app

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
async def test_verify_email_success(storage_service):
    email = "test.user@maine.edu"
    valid_token = generate_verification_token(email)
    
    #Using storage_Service register the email 
    user_id = await storage_service.register_user(email)
    assert user_id
    
    # Test
    async with app.test_client() as client:
        response = await client.get(f"/verify/verify-email?token={valid_token}")
        assert response.status_code == 200
        
        json_data = await response.get_json()
        assert json_data["message"] == "email has been successfully verified"
        
        #Tries to get the user from user ID to check if in database
        Verified_user = await storage_service.get_user(user_id)
        
        assert Verified_user

        assert Verified_user.verified is True