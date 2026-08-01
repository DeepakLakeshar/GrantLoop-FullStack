"""
Stateless, signed password-reset tokens — no database table, per the
GrantLoop v1.1 Auth/Anonymity/Notifications architecture doc. A token
encodes the user id, is HMAC-signed with SECRET_KEY, and self-expires
via PASSWORD_RESET_TIMEOUT. Nothing to clean up, nothing to leak from a
token table.
"""
from django.core import signing
from django.core.signing import BadSignature, SignatureExpired

SALT = "grantloop-password-reset"


def generate_password_reset_token(user_id: str) -> str:
    return signing.dumps({"user_id": str(user_id)}, salt=SALT)


def verify_password_reset_token(token: str, max_age: int) -> str | None:
    try:
        data = signing.loads(token, salt=SALT, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None
    return data.get("user_id")
