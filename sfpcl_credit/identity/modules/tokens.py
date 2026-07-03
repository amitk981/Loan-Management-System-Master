"""JWT token encoding, decoding, and claim construction for auth sessions.

PyJWT HS256 signed with `settings.SECRET_KEY`. Lifetimes and claims are the
002B/002B2 contract and must not change here — this module only isolates the
token mechanics behind an explicit interface so views and the auth service
depend on named functions rather than inline crypto.
"""

import hashlib
import uuid

import jwt
from django.conf import settings
from django.utils import timezone


class TokenError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(message)


def encode_token(claims):
    return jwt.encode(claims, settings.SECRET_KEY, algorithm="HS256")


def decode_token(token, expected_type):
    try:
        claims = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
            options={"require": ["exp"]},
        )
    except jwt.ExpiredSignatureError as exc:
        code = "REFRESH_TOKEN_EXPIRED" if expected_type == "refresh" else "TOKEN_EXPIRED"
        raise TokenError(code, "Token has expired.") from exc
    except jwt.InvalidSignatureError as exc:
        raise TokenError("INVALID_TOKEN", "Token signature is invalid.") from exc
    except jwt.DecodeError as exc:
        raise TokenError("INVALID_TOKEN", "Token format is invalid.") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenError("INVALID_TOKEN", "Token is invalid.") from exc

    if claims.get("token_type") != expected_type:
        raise TokenError("INVALID_TOKEN", "Token type is invalid.")
    return claims


def hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def access_claims(user, session):
    now = timezone.now()
    exp = now + timezone.timedelta(minutes=settings.AUTH_ACCESS_TOKEN_MINUTES)
    return {
        "token_type": "access",
        "user_id": str(user.user_id),
        "session_id": str(session.user_session_id),
        "email": user.email,
        "role_codes": user.role_codes(),
        "team_codes": user.team_codes(),
        "permissions_version": user.permissions_version(),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }


def refresh_claims(session):
    now = timezone.now()
    return {
        "token_type": "refresh",
        "user_id": str(session.user_id),
        "session_id": str(session.user_session_id),
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int(session.expires_at.timestamp()),
    }
