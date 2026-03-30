import pytest

pytestmark = pytest.mark.asyncio


async def test_submit_survey_success(authenticated_client):
    """Verify that an authenticated user can submit a survey."""
    data = {"num_participants": 5, "experience": 4, "other_thoughts": "Everything was great!", "foodshare_fk_id": None}

    response = await authenticated_client.post("/surveys", json=data)
    assert response.status_code == 201
    res_json = await response.get_json()
    assert res_json["success"] is True
    assert "survey_id" in res_json


async def test_submit_survey_missing_fields(authenticated_client):
    """Verify that missing required survey fields result in a 400 error."""
    # num_participants is required
    data = {"experience": 4}

    response = await authenticated_client.post("/surveys", json=data)
    assert response.status_code == 400
    assert (await response.get_json())["error"] == "Missing required fields: 'num_participants' and 'experience'"


async def test_get_all_surveys_admin_only(authenticated_client, admin_client):
    """Verify that only admins can retrieve all surveys."""
    # 1. Access as regular user
    response = await authenticated_client.get("/surveys")
    assert response.status_code == 403

    # 2. Access as admin
    # First submit one survey
    await admin_client.post(
        "/surveys", json={"num_participants": 10, "experience": 5, "other_thoughts": "Admin survey"}
    )

    response = await admin_client.get("/surveys")
    assert response.status_code == 200
    res_json = await response.get_json()
    assert len(res_json) >= 1
    assert res_json[0]["num_participants"] == 10
    assert res_json[0]["experience"] == 5
    assert res_json[0]["other_thoughts"] == "Admin survey"
