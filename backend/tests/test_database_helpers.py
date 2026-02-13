from src.database import (
    User,
    unpack_picture_from_row,
    unpack_user_from_row,
    validate_email_format,
)


def test_email_validation():
    assert validate_email_format("test@maine.edu")
    assert validate_email_format("firstname.lastname@maine.edu")
    assert not validate_email_format("")
    assert not validate_email_format("firstname.lastname@unrelated.com")
    assert not validate_email_format("firstname.lastname@bad.edu")
    assert not validate_email_format("firstname.lastname@malicious.maine.edu")


def test_unpack_user():
    test_user = {
        "user_id": 0,
        "email": "first.last@maine.edu",
        "verified": 0,
        "banned": 0,
    }
    expect_user = User(
        user_id=0, email="first.last@maine.edu", verified=False, banned=False
    )
    assert unpack_user_from_row(test_user) == expect_user
