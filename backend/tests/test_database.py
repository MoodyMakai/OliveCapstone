import pytest

from src.database import DatabaseManager


@pytest.mark.asyncio
async def test_add_user(db_manager: DatabaseManager):
    email = "first.last@maine.edu"
    await db_manager.add_user(email)
    user = await db_manager.get_user_by_email(email)
    if user is None:
        pytest.fail()
    assert user.email == email
    assert not user.verified
    assert not user.banned


@pytest.mark.asyncio
async def test_get_user(db_manager: DatabaseManager):
    emails = ["first.last@maine.edu", "another@maine.edu"]
    for email in emails:
        await db_manager.add_user(email)
    await db_manager.add_user("bad@email.com")  # add a bad email

    # test that the good users are there
    # MARK: Add changing user verification and banned status
    for email in emails:
        user = await db_manager.get_user_by_email(email)
        if user is None:
            pytest.fail()
        assert user.email == email
        assert not user.verified
        assert not user.banned
    bad_user = await db_manager.get_user_by_email("bad@email.com")
    assert bad_user is None
