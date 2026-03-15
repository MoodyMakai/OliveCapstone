import hashlib
from datetime import datetime, timedelta

import pytest

# Assuming your original code is saved in a file named 'db_helpers.py'
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


class TestDataClasses:
    def test_user_initialization_and_defaults(self):
        user = User(user_id=1, email="test@maine.edu")
        assert user.user_id == 1
        assert user.email == "test@maine.edu"
        assert user.verified is False
        assert user.banned is False
        assert user.is_admin is False

    def test_otp_record_initialization(self):
        now = datetime.now()
        otp = OTPRecord(email="test@maine.edu", otp="123456", expires_at=now)
        assert otp.email == "test@maine.edu"
        assert otp.otp == "123456"
        assert otp.expires_at == now

    def test_device_session_initialization(self):
        session = DeviceSession(user_id=1, banned=0)
        assert session.user_id == 1
        assert session.banned == 0

    def test_picture_metadata_initialization(self):
        now = datetime.now()
        pic = PictureMetadata(picture_id=10, expires=now, filepath="/imgs/1.jpg", mimetype="image/jpeg")
        assert pic.picture_id == 10
        assert pic.filepath == "/imgs/1.jpg"
        assert pic.mimetype == "image/jpeg"

    def test_foodshare_initialization_and_defaults(self):
        now = datetime.now()
        fs = Foodshare(foodshare_id=1, name="Pizza", location="Union", ends=now, restrictions=["dairy"], active=True)
        assert fs.foodshare_id == 1
        assert fs.creator is None
        assert fs.picture is None

    def test_foodshare_with_nested_objects(self):
        user = User(user_id=1, email="test@maine.edu")
        pic = PictureMetadata(picture_id=1, expires=datetime.now(), filepath="/a.jpg", mimetype="image/jpeg")
        fs = Foodshare(
            foodshare_id=1,
            name="Pizza",
            location="Union",
            ends=datetime.now(),
            restrictions=[],
            active=True,
            creator=user,
            picture=pic,
        )
        assert fs.creator
        assert fs.picture
        assert fs.creator.email == "test@maine.edu"
        assert fs.picture.picture_id == 1

    def test_survey_initialization_and_defaults(self):
        survey = Survey(survey_id=1, num_participants=5, experience=4, other_thoughts="Great!")
        assert survey.survey_id == 1
        assert survey.foodshare is None


class TestUtilityFunctions:
    @pytest.mark.parametrize(
        "email",
        [
            "student@maine.edu",
            "john.doe123@maine.edu",
            "student+food@maine.edu",
            "STUDENT@MAINE.EDU",
            "a.b.c@maine.edu",
        ],
    )
    def test_validate_email_format_valid(self, email):
        assert validate_email_format(email) is True

    @pytest.mark.parametrize(
        "email",
        [
            "student@gmail.com",
            "student@maine.edu.org",
            "student@maine.com",
            "studentmaine.edu",
            "st!udent@maine.edu",
            "student @maine.edu",
            "@",
            "",
            None,
        ],
    )
    def test_validate_email_format_invalid(self, email):
        # We need to catch potential TypeErrors if the function doesn't handle None perfectly
        # but based on the code provided (`if not email or "@" not in email:`), None will fail
        # safely without an exception because Python evaluates 'not None' as True.
        assert validate_email_format(email) is False

    @pytest.mark.parametrize(
        "input_str, expected",
        [
            ("Hello World", "Hello World"),
            ("  Hello World  ", "Hello World"),  # Strip whitespace
            ("a" * 600, "a" * 500),  # Length truncation
        ],
    )
    def test_sanitize_string_valid(self, input_str, expected):
        assert sanitize_string(input_str) == expected

    @pytest.mark.parametrize("input_str", [123, ["list"], None, {}])
    def test_sanitize_string_invalid_types(self, input_str):
        assert sanitize_string(input_str) == ""

    @pytest.mark.parametrize(
        "date_input", ["2023-10-25T12:00:00", "2023-10-25T12:00:00+00:00", "2023-10-25", datetime.now()]
    )
    def test_validate_datetime_format_valid(self, date_input):
        assert validate_datetime_format(date_input) is True

    @pytest.mark.parametrize("date_input", ["10/25/2023", "not a date", ""])
    def test_validate_datetime_format_invalid(self, date_input):
        # We need to expect exceptions for invalid types
        assert validate_datetime_format(date_input) is False

    # --- hash_token ---
    def test_hash_token_consistency(self):
        token = "my_secret_token"
        assert hash_token(token) == hash_token(token)

    def test_hash_token_format_and_length(self):
        token = "test_token"
        hashed = hash_token(token)
        assert len(hashed) == 64
        # Verify it's a valid hex string
        int(hashed, 16)

    def test_hash_token_empty_string(self):
        # The SHA-256 hash of an empty string is a known constant
        empty_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert hash_token("") == empty_hash

    # --- generate_secure_token ---
    def test_generate_secure_token_length(self):
        token = generate_secure_token()
        assert isinstance(token, str)
        # 32 bytes URL-safe base64 encoded will be ~43 characters long
        assert len(token) >= 43

    def test_generate_secure_token_uniqueness(self):
        # Generate 100 tokens and ensure they are all unique using a set
        tokens = {generate_secure_token() for _ in range(100)}
        assert len(tokens) == 100

    def test_generate_secure_token_url_safe(self):
        token = generate_secure_token()
        # Make sure no standard base64 unsafe characters are present
        assert "+" not in token
        assert "/" not in token
