from itsdangerous import URLSafeTimedSerializer

# Temp Secret key For Dev, Replace with a more secure method
SECRET_KEY = "Apples-To-Oranges"
SALT = "Email-Verification-Test"


def get_serializer():
    return URLSafeTimedSerializer(SECRET_KEY)


def generate_verification_token(email: str) -> str:
    serializer = get_serializer()
    return serializer.dumps(email, salt=SALT)


def verify_verification_token(token: str, expiry: int = 1800):
    serializer = get_serializer()
    try:
        email = serializer.loads(token, salt=SALT, max_age=expiry)
        return email
    except Exception:
        return None
