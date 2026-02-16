from database import validate_email_format
from tokens import generate_verification_token

# Web link for validation
domain = "https://localhost:5000/verify-email"


def create_user_verification_token(email: str) -> str | None:
    if not validate_email_format(email):
        return None
    return generate_verification_token(email)


def build_verification_link(token: str) -> str:
    # returns the link with the query ?token={token} on the end
    return f"{domain}?token={token}"


def create_user_verification_link(email: str) -> str | None:
    token = create_user_verification_token(email)
    if not token:
        return None
    return build_verification_link(token)
