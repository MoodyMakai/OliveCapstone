import pytest

from src.database import DatabaseManager


async def fill_users_table(db_manager: DatabaseManager, emails: list) -> list[int | None]:
    user_ids = []
    for email in emails:
        uid = await db_manager.add_user(email)
        user_ids.append(uid)
    return user_ids


@pytest.mark.asyncio
async def test_add_user(db_manager: DatabaseManager):
    email = "first.last@maine.edu"
    await db_manager.add_user(email)
    user = await db_manager.get_user_by_email(email)
    assert user
    assert user.email == email
    assert not user.verified
    assert not user.banned


@pytest.mark.asyncio
async def test_get_user(db_manager: DatabaseManager):
    emails = ["first.last@maine.edu", "f.last@maine.edu", "john.doe@maine.edu"]
    user_ids = await fill_users_table(db_manager, emails)

    for uid in user_ids:
        assert uid
        user = await db_manager.get_user(uid)
        assert user
        assert user.email == emails[uid - 1]
        assert not user.verified
        assert not user.banned


@pytest.mark.asyncio
async def test_get_user_by_email(db_manager: DatabaseManager):
    emails = ["first.last@maine.edu", "f.last@maine.edu", "john.doe@maine.edu"]
    await fill_users_table(db_manager, emails)

    for email in emails:
        user = await db_manager.get_user_by_email(email)
        assert user
        assert user.email == email
        assert not user.verified
        assert not user.banned


@pytest.mark.asyncio
async def test_update_status(db_manager: DatabaseManager):
    emails = ["first.last@maine.edu", "f.last@maine.edu", "john.doe@maine.edu"]
    user_ids = await fill_users_table(db_manager, emails)
    for uid in user_ids:
        assert uid
        await db_manager.update_user_status(uid, True, None)
    for uid in user_ids:
        assert uid
        user = await db_manager.get_user(uid)
        assert user
        assert user.verified
        assert not user.banned
    for uid in user_ids:
        assert uid
        await db_manager.update_user_status(uid, None, True)
    for uid in user_ids:
        if uid is None:
            pytest.fail()
        user = await db_manager.get_user(uid)
        assert user
        assert user.verified
        assert user.banned


@pytest.mark.asyncio
async def test_delete_user(db_manager: DatabaseManager):
    emails = ["first.last@maine.edu", "f.last@maine.edu", "john.doe@maine.edu"]
    await fill_users_table(db_manager, emails)
    await db_manager.delete_user_by_id(1)
    assert await db_manager.get_user(2)
    assert await db_manager.get_user(3)
    assert not await db_manager.get_user(1)
