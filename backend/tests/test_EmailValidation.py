import pytest

import src.tokens as tokens
from src.database_helpers import validate_email_format

# Test emails add or remove as you would like, this shouldn't affect validty of testing.
# An Full email List, a valid and invalid list for testing emails.

EMAILS = [
    "first.last@maine.edu",
    "last.first@maine.edu",
    "Michael.Jordan@MAINE.EDU",
    "Bad.Actor@Maine.EdU",
    "first.last@aol.com",
    "ImAHacker.LetmeIn@Steal.com",
    "Yohoho@maine.edu.m",
    "Givemeyourdata@gmail.com",
    "Prof.Yoo@maine.edu",
]

valid_emails = [
    "first.last@maine.edu",
    "last.first@maine.edu",
    "Michael.Jordan@MAINE.EDU",
    "Bad.Actor@Maine.EdU",
]
invalid_emails = [
    "first.last@aol.com",  # Wrong Domain Invalid
    "ImAHacker.LetmeIn@Steal.com",  # Wrong Domain
    "Yohoho@maine.edu.m",  # Error in domain
    "Givemeyourdata@gmail.com",
]


def test_generate_token():
    for email in EMAILS:
        token = tokens.generate_verification_token(email)
        # Empty Case
        if not token:
            pytest.fail(f"{email} broke the token genrator")
        assert isinstance(token, str)


def test_verify_token():
    for email in EMAILS:
        token = tokens.generate_verification_token(email)
        verified = tokens.verify_verification_token(token)
        if verified is None:
            pytest.fail(f"{token} Failed Verification Process")
        assert verified == email


def test_email_verification():
    for email in valid_emails:
        result = validate_email_format(email)
        assert result is True, f"{email} Accepted when Invalid"

    for email in invalid_emails:
        result = validate_email_format(email)
        assert result is False, f"{email} rejected when it is valid."


def test_email_verification_entire():
    for email in EMAILS:
        result = validate_email_format(email)
        if not result:
            continue
        # If the Email is not umaine, no need to validate token
        else:
            token = tokens.generate_verification_token(email)
            verified_email = tokens.verify_verification_token(token)
            # Tests for empty token, token is string, and the verified email is same.
            assert token is not None, f"{token} broke the token generator"

            assert isinstance(token, str), f"{token} isn't a string"

            assert verified_email == email, f"{token} failed verification"
