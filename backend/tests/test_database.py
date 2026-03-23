from datetime import UTC, datetime, timedelta

import pytest

from src.database_helpers import DeviceSession, Foodshare, OTPRecord, PictureMetadata, Survey, User

# Mark all tests in this file as async
pytestmark = pytest.mark.asyncio


### A. Connection & Initialization ###


async def test_tables_initialized(db_manager):
    """Verify that the fixture correctly initializes the database tables."""
    async with db_manager.conn.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
        tables = [row["name"] for row in await cursor.fetchall()]

    # Check for a few core tables expected from init_tables.sql
    assert "users" in tables
    assert "pictures" in tables
    assert "foodshares" in tables


### B. User Management ###


async def test_add_user(db_manager):
    """Test adding a new user returns a valid integer ID."""
    user_id = await db_manager.add_user("test@maine.edu")
    assert isinstance(user_id, int)
    assert user_id > 0


async def test_get_user_exists(db_manager):
    """Test retrieving an existing user by ID."""
    user_id = await db_manager.add_user("get_test@maine.edu", verified=True)
    user = await db_manager.get_user(user_id)

    assert user is not None
    assert isinstance(user, User)
    assert user.email == "get_test@maine.edu"
    assert user.verified is True
    assert user.banned is False


async def test_get_user_not_found(db_manager):
    """Test retrieving a non-existent user returns None."""
    user = await db_manager.get_user(99999)
    assert user is None


async def test_get_user_by_email(db_manager):
    """Test retrieving a user by their email address."""
    await db_manager.add_user("email_test@maine.edu")
    user = await db_manager.get_user_by_email("email_test@maine.edu")

    assert user is not None
    assert user.email == "email_test@maine.edu"


async def test_update_user_status(db_manager):
    """Test updating the verified and banned status of a user."""
    user_id = await db_manager.add_user("update_test@maine.edu")

    # Update both statuses
    await db_manager.update_user_status(user_id, verified=True, banned=True)
    updated_user = await db_manager.get_user(user_id)

    assert updated_user.verified is True
    assert updated_user.banned is True

    # Update only one status
    await db_manager.update_user_status(user_id, banned=False)
    re_updated_user = await db_manager.get_user(user_id)

    assert re_updated_user.verified is True  # Should remain unchanged
    assert re_updated_user.banned is False


async def test_delete_user_by_id(db_manager):
    """Test deleting a user removes them from the database."""
    user_id = await db_manager.add_user("delete_test@maine.edu")
    await db_manager.delete_user_by_id(user_id)

    user = await db_manager.get_user(user_id)
    assert user is None


async def test_create_or_verify_user(db_manager):
    """Test creating a new user or verifying an existing one."""
    email = "verify_test@maine.edu"

    # 1. Create phase: User does not exist yet
    user_id_1 = await db_manager.create_or_verify_user(email)
    user_1 = await db_manager.get_user(user_id_1)

    assert user_1 is not None
    assert user_1.email == email
    assert user_1.verified is True  # create_or_verify_user sets verified=1 on insert

    # 2. Verify phase: User already exists
    # First, manually un-verify them to test the update logic
    await db_manager.update_user_status(user_id_1, verified=False)

    user_id_2 = await db_manager.create_or_verify_user(email)
    user_2 = await db_manager.get_user(user_id_2)

    assert user_id_1 == user_id_2  # Should return the same user ID
    assert user_2.verified is True  # Should be updated back to True


### C. Picture Management ###


async def test_add_and_get_picture(db_manager):
    """Test adding a picture and retrieving its metadata."""
    future_date = datetime.now(tz=UTC) + timedelta(days=1)

    picture_id = await db_manager.add_picture(expires=future_date, filepath="/images/test.jpg", mimetype="image/jpeg")

    picture = await db_manager.get_picture(picture_id)

    assert picture is not None
    assert isinstance(picture, PictureMetadata)
    assert picture.filepath == "/images/test.jpg"
    assert picture.mimetype == "image/jpeg"


async def test_get_picture_not_found(db_manager):
    """Test retrieving a non-existent picture returns None."""
    picture = await db_manager.get_picture(99999)
    assert picture is None


async def test_delete_expired_pictures(db_manager):
    """Test that only expired pictures are deleted and their filepaths returned."""
    past_date = datetime.now(tz=UTC) - timedelta(days=1)
    future_date = datetime.now(tz=UTC) + timedelta(days=1)

    # Add an expired picture
    expired_id = await db_manager.add_picture(past_date, "/images/expired.jpg", "image/jpeg")
    # Add a valid picture
    valid_id = await db_manager.add_picture(future_date, "/images/valid.jpg", "image/jpeg")

    deleted_filepaths = await db_manager.delete_expired_pictures()

    # Verify the expired picture filepath was returned
    assert len(deleted_filepaths) == 1
    assert "/images/expired.jpg" in deleted_filepaths

    # Verify DB state
    assert await db_manager.get_picture(expired_id) is None
    assert await db_manager.get_picture(valid_id) is not None


### D. Foodshare Management ###


async def test_add_and_get_foodshare_basic(db_manager):
    """Test adding a basic foodshare without foreign keys (creator/picture)."""
    ends_date = datetime.now(tz=UTC) + timedelta(hours=2)

    fs_id = await db_manager.add_foodshare(name="Free Pizza", location="Student Union", ends=ends_date, active=True)

    foodshare = await db_manager.get_foodshare(fs_id)

    assert foodshare is not None
    assert isinstance(foodshare, Foodshare)
    assert foodshare.name == "Free Pizza"
    assert foodshare.location == "Student Union"
    assert foodshare.active is True
    assert foodshare.creator is None
    assert foodshare.picture is None
    assert foodshare.restrictions == []


async def test_add_and_get_foodshare_with_fks(db_manager):
    """Test adding a foodshare with a creator and picture linked."""
    # 1. Setup foreign key dependencies
    user_id = await db_manager.add_user("creator@maine.edu")
    pic_id = await db_manager.add_picture(datetime.now(tz=UTC) + timedelta(days=1), "/images/pizza.jpg", "image/jpeg")

    # 2. Add foodshare
    fs_id = await db_manager.add_foodshare(
        name="Donuts",
        location="Library",
        ends=datetime.now(tz=UTC) + timedelta(hours=1),
        active=True,
        user_fk_id=user_id,
        picture_fk_id=pic_id,
    )

    foodshare = await db_manager.get_foodshare(fs_id)

    # 3. Assert relations are populated
    assert foodshare is not None
    assert foodshare.creator is not None
    assert foodshare.creator.email == "creator@maine.edu"
    assert foodshare.picture is not None
    assert foodshare.picture.filepath == "/images/pizza.jpg"


async def test_foodshare_restrictions(db_manager):
    """Test creating restrictions and linking them to a foodshare."""
    fs_id = await db_manager.add_foodshare("Bagels", "Lobby", datetime.now(tz=UTC) + timedelta(hours=1), True)

    # Add restrictions
    await db_manager.add_restriction_to_foodshare_by_name(fs_id, "Gluten-Free")
    await db_manager.add_restriction_to_foodshare_by_name(fs_id, "Vegan")

    # Test idempotency of get_or_create_restriction (adding the same one again)
    await db_manager.add_restriction_to_foodshare_by_name(fs_id, "Vegan")

    foodshare = await db_manager.get_foodshare(fs_id)

    assert len(foodshare.restrictions) == 2
    assert "Gluten-Free" in foodshare.restrictions
    assert "Vegan" in foodshare.restrictions


async def test_get_all_active_foodshares(db_manager):
    """Test retrieving only the active foodshares."""
    ends_date = datetime.now(tz=UTC) + timedelta(hours=1)

    # Add 2 active, 1 inactive
    await db_manager.add_foodshare("Active 1", "Loc 1", ends_date, active=True)
    await db_manager.add_foodshare("Inactive", "Loc 2", ends_date, active=False)
    await db_manager.add_foodshare("Active 2", "Loc 3", ends_date, active=True)

    active_shares = await db_manager.get_all_active_foodshares()

    assert len(active_shares) == 2
    names = [fs.name for fs in active_shares]
    assert "Active 1" in names
    assert "Active 2" in names
    assert "Inactive" not in names


async def test_deactivate_foodshare(db_manager):
    """Test setting a foodshare to inactive."""
    fs_id = await db_manager.add_foodshare("Tacos", "Quad", datetime.now(tz=UTC) + timedelta(hours=1), active=True)

    # Verify active first
    fs_before = await db_manager.get_foodshare(fs_id)
    assert fs_before.active is True

    # Deactivate
    await db_manager.deactivate_foodshare(fs_id)

    # Verify inactive
    fs_after = await db_manager.get_foodshare(fs_id)
    assert fs_after.active is False


### E. Survey Management ###


async def test_add_and_get_survey(db_manager):
    """Test adding a survey linked to a foodshare and retrieving it."""
    # 1. Setup foodshare dependency
    fs_id = await db_manager.add_foodshare(
        name="Survey Pizza", location="Room 101", ends=datetime.now(tz=UTC) + timedelta(hours=1), active=True
    )

    # 2. Add survey
    survey_id = await db_manager.add_survey(
        num_participants=5, experience=4, other_thoughts="It was great!", foodshare_fk_id=fs_id
    )

    # 3. Retrieve and assert
    survey = await db_manager.get_survey(survey_id)

    assert survey is not None
    assert isinstance(survey, Survey)
    assert survey.num_participants == 5
    assert survey.experience == 4
    assert survey.other_thoughts == "It was great!"
    assert survey.foodshare is not None
    assert survey.foodshare.name == "Survey Pizza"


async def test_get_all_surveys(db_manager):
    """Test retrieving all surveys in the database."""
    # Add surveys without linking them to a foodshare (testing optional FK)
    await db_manager.add_survey(2, 5, "Awesome", None)
    await db_manager.add_survey(1, 3, "Okay", None)

    surveys = await db_manager.get_all_surveys()

    assert len(surveys) == 2
    assert any(s.other_thoughts == "Awesome" for s in surveys)
    assert any(s.other_thoughts == "Okay" for s in surveys)


### F. Authentication & Sessions (OTPs and Device Tokens) ###


async def test_save_and_get_otp(db_manager):
    """Test saving a new OTP record and retrieving it."""
    expires = datetime.now(tz=UTC) + timedelta(minutes=10)
    email = "otp_test@maine.edu"

    otp_record = OTPRecord(email=email, otp="123456", expires_at=expires)
    await db_manager.save_otp(otp_record)

    fetched_otp = await db_manager.get_otp(email)

    assert fetched_otp is not None
    assert isinstance(fetched_otp, OTPRecord)
    assert fetched_otp.email == email
    assert fetched_otp.otp == "123456"
    assert isinstance(fetched_otp.expires_at, datetime)


async def test_update_otp_on_conflict(db_manager):
    """Test that saving an OTP for an existing email updates the record instead of crashing."""
    email = "conflict@maine.edu"

    # Initial OTP
    expires1 = datetime.now(tz=UTC) + timedelta(minutes=10)
    await db_manager.save_otp(OTPRecord(email=email, otp="111111", expires_at=expires1))

    # New OTP for the same email
    expires2 = datetime.now(tz=UTC) + timedelta(minutes=20)
    await db_manager.save_otp(OTPRecord(email=email, otp="222222", expires_at=expires2))

    fetched_otp = await db_manager.get_otp(email)

    assert fetched_otp is not None
    assert fetched_otp.otp == "222222"  # Should reflect the updated OTP


async def test_delete_otp(db_manager):
    """Test deleting an OTP record by email."""
    email = "delete_otp@maine.edu"
    expires = datetime.now(tz=UTC) + timedelta(minutes=10)

    await db_manager.save_otp(OTPRecord(email=email, otp="999999", expires_at=expires))
    await db_manager.delete_otp(email)

    fetched_otp = await db_manager.get_otp(email)
    assert fetched_otp is None


async def test_device_tokens_and_sessions(db_manager):
    """Test creating a token and fetching the associated session/user."""
    user_id = await db_manager.add_user("session@maine.edu", verified=True)
    token_hash = "secure_hash_xyz_123"

    # Create token
    await db_manager.create_device_token(user_id, token_hash)

    # Test get_session_by_token
    session = await db_manager.get_session_by_token(token_hash)
    assert session is not None
    assert isinstance(session, DeviceSession)
    assert session.user_id == user_id
    assert session.banned == 0  # Matches default from add_user

    # Test get_user_by_token
    user = await db_manager.get_user_by_token(token_hash)
    assert user is not None
    assert user.email == "session@maine.edu"


async def test_update_token_usage(db_manager):
    """Test updating the last_used timestamp for a token."""
    user_id = await db_manager.add_user("usage@maine.edu")
    token_hash = "usage_hash_456"
    await db_manager.create_device_token(user_id, token_hash)

    # Because `last_used` isn't mapped directly to our dataclasses,
    # we test that these run successfully without raising SQLite exceptions.
    try:
        await db_manager.update_token_usage(token_hash)
        await db_manager.reset_token_lifetime(token_hash)
        success = True
    except Exception:
        success = False

    assert success is True
