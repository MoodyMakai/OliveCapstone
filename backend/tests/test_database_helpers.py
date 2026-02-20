from src.database_helpers import (
    validate_email_format,
)


def test_email_validation():
    assert validate_email_format("test@maine.edu")
    assert validate_email_format("firstname.lastname@maine.edu")
    assert not validate_email_format("")
    assert not validate_email_format("firstname.lastname@unrelated.com")
    assert not validate_email_format("firstname.lastname@bad.edu")
    assert not validate_email_format("firstname.lastname@malicious.maine.edu")
