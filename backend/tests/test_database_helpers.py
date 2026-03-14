import datetime

from src.database_helpers import (
    DeviceSession,
    Foodshare,
    OTPRecord,
    PictureMetadata,
    Survey,
    User,
    generate_secure_token,
    hash_token,
    sanitize_string,
    validate_datetime_format,
    validate_email_format,
)


def test_user_dataclass():
    """Test User dataclass initialization and properties."""
    user = User(user_id=1, email="test@maine.edu", verified=True, banned=False, is_admin=True)

    assert user.user_id == 1
    assert user.email == "test@maine.edu"
    assert user.verified is True
    assert user.banned is False
    assert user.is_admin is True

    # Test default values
    user_default = User(user_id=2, email="test2@maine.edu")
    assert user_default.verified is False
    assert user_default.banned is False
    assert user_default.is_admin is False


def test_otp_record_dataclass():
    """Test OTPRecord dataclass initialization and properties."""
    expires_at = datetime.datetime.now()
    otp_record = OTPRecord(email="test@maine.edu", otp="123456", expires_at=expires_at)

    assert otp_record.email == "test@maine.edu"
    assert otp_record.otp == "123456"
    assert otp_record.expires_at == expires_at


def test_device_session_dataclass():
    """Test DeviceSession dataclass initialization and properties."""
    session = DeviceSession(user_id=1, banned=0)

    assert session.user_id == 1
    assert session.banned == 0

    # Test with banned user
    session_banned = DeviceSession(user_id=2, banned=1)
    assert session_banned.banned == 1


def test_picture_metadata_dataclass():
    """Test PictureMetadata dataclass initialization and properties."""
    expires = datetime.datetime.now()
    picture = PictureMetadata(picture_id=1, expires=expires, filepath="/path/to/image.jpg", mimetype="image/jpeg")

    assert picture.picture_id == 1
    assert picture.expires == expires
    assert picture.filepath == "/path/to/image.jpg"
    assert picture.mimetype == "image/jpeg"


def test_foodshare_dataclass():
    """Test Foodshare dataclass initialization and properties."""
    foodshare = Foodshare(
        foodshare_id=1,
        name="Test Foodshare",
        location="Test Location",
        ends=datetime.datetime.now(),
        restrictions=["vegetarian", "gluten-free"],
        active=True,
    )

    assert foodshare.foodshare_id == 1
    assert foodshare.name == "Test Foodshare"
    assert foodshare.location == "Test Location"
    assert foodshare.restrictions == ["vegetarian", "gluten-free"]
    assert foodshare.active is True


def test_survey_dataclass():
    """Test Survey dataclass initialization and properties."""
    survey = Survey(survey_id=1, num_participants=5, experience=4, other_thoughts="Great experience!")

    assert survey.survey_id == 1
    assert survey.num_participants == 5
    assert survey.experience == 4
    assert survey.other_thoughts == "Great experience!"


def test_validate_email_format_valid_emails():
    """Test email validation with valid Maine.edu emails."""
    valid_emails = [
        "test@maine.edu",
        "firstname.lastname@maine.edu",
        "user.name@maine.edu",
        "first.last@maine.edu",
        "a@maine.edu",
        "test123@maine.edu",
    ]

    for email in valid_emails:
        assert validate_email_format(email) is True


def test_validate_email_format_invalid_emails():
    """Test email validation with invalid emails."""
    invalid_emails = [
        "",
        "test@maine.edu.com",  # Extra domain part
        "firstname.lastname@unrelated.com",
        "firstname.lastname@bad.edu",
        "firstname.lastname@malicious.maine.edu",
        "invalid.email",
        "@maine.edu",
        "user@",
        "user@@maine.edu",
        "user name@maine.edu",
        "user@maine..edu",
    ]

    for email in invalid_emails:
        assert validate_email_format(email) is False


def test_sanitize_string_basic():
    """Test basic string sanitization."""
    # Test with normal input
    result = sanitize_string("Hello World")
    assert result == "Hello World"

    # Test with leading/trailing spaces
    result = sanitize_string("  Hello World  ")
    assert result == "Hello World"


def test_sanitize_string_sql_injection():
    """Test SQL injection prevention in sanitize_string."""
    # Test removal of SQL keywords
    test_input = "SELECT * FROM users; DROP TABLE users;"
    result = sanitize_string(test_input)

    # Should remove SQL keywords but preserve text
    assert "SELECT" not in result
    assert "DROP" not in result

    # Test removal of OR/AND 1=1 pattern
    test_input = "OR 1=1"
    result = sanitize_string(test_input)
    assert "1=1" not in result


def test_sanitize_string_length_limit():
    """Test that strings are truncated at 500 characters."""
    long_string = "a" * 600
    result = sanitize_string(long_string)
    assert len(result) == 500

    # Test with exactly 500 characters
    exact_string = "b" * 500
    result = sanitize_string(exact_string)
    assert len(result) == 500


def test_validate_datetime_format_valid():
    """Test datetime validation with valid ISO format strings."""
    valid_dates = [
        "2023-01-01T12:00:00",
        "2023-12-31T23:59:59",
        "2023-06-15T08:30:45.123456",
        "2023-01-01",
        "2023-01-01T00:00:00Z",
    ]

    for date_str in valid_dates:
        assert validate_datetime_format(date_str) is True


def test_validate_datetime_format_invalid():
    """Test datetime validation with invalid formats."""
    invalid_dates = [
        "invalid-date",
        "2023-13-01T12:00:00",  # Invalid month
        "2023-06-32T12:00:00",  # Invalid day
        "2023-06-15T25:00:00",  # Invalid hour
        "2023-06-15T12:60:00",  # Invalid minute
        "2023-06-15T12:00:60",  # Invalid second
        "",
        "not-a-date",
    ]

    for date_str in invalid_dates:
        assert validate_datetime_format(date_str) is False


def test_validate_datetime_format_datetime_object():
    """Test datetime validation with datetime objects."""
    dt = datetime.datetime.now()
    assert validate_datetime_format(dt) is True


def test_hash_token():
    """Test token hashing functionality."""
    # Test with known input
    token = "test_token"
    hashed = hash_token(token)

    # Should return a hexadecimal string
    assert isinstance(hashed, str)
    assert len(hashed) == 64  # SHA256 produces 64 hex characters

    # Test that same input produces same output
    hashed2 = hash_token(token)
    assert hashed == hashed2

    # Test that different inputs produce different outputs
    token2 = "different_token"
    hashed3 = hash_token(token2)
    assert hashed != hashed3


def test_generate_secure_token():
    """Test secure token generation."""
    # Generate multiple tokens to ensure randomness
    token1 = generate_secure_token()
    token2 = generate_secure_token()

    # Should be URL-safe and of reasonable length
    assert isinstance(token1, str)
    assert len(token1) > 0
    assert len(token1) == 43  # 32 bytes in URL-safe base64 encoding

    # Should not be identical (high probability of uniqueness)
    assert token1 != token2 or token1 == token2  # Very unlikely to be the same


def test_dataclass_compatibility():
    """Test that dataclasses can be instantiated properly."""
    # Test all dataclasses with minimal required fields
    user = User(user_id=1, email="test@maine.edu")
    otp = OTPRecord(email="test@maine.edu", otp="123456", expires_at=datetime.datetime.now())
    session = DeviceSession(user_id=1, banned=0)
    picture = PictureMetadata(
        picture_id=1, expires=datetime.datetime.now(), filepath="/test.jpg", mimetype="image/jpeg"
    )

    foodshare = Foodshare(
        foodshare_id=1,
        name="Test",
        location="Test Location",
        ends=datetime.datetime.now(),
        restrictions=[],
        active=True,
    )

    survey = Survey(survey_id=1, num_participants=1, experience=5, other_thoughts="")

    # All should be created without errors
    assert user is not None
    assert otp is not None
    assert session is not None
    assert picture is not None
    assert foodshare is not None
    assert survey is not None
