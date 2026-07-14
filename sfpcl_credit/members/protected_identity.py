import hashlib
import hmac

from django.conf import settings


def identity_hash(value):
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        value.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def protected_identity_token(value, expected_length):
    digest = identity_hash(f"enc:{value}")
    return f"enc:v1:{expected_length}:{digest}:{value[-4:]}"


def mask_protected_identity(token, default_length):
    parts = str(token or "").split(":")
    if len(parts) == 7 and parts[0] == "seal" and parts[1] == "v1":
        try:
            length = int(parts[2])
        except ValueError:
            length = default_length
        return f"{'*' * max(length - 4, 0)}{parts[6]}"
    if len(parts) == 5 and parts[0] == "enc" and parts[1] == "v1":
        try:
            length = int(parts[2])
        except ValueError:
            length = default_length
        return f"{'*' * max(length - 4, 0)}{parts[4]}"
    text = str(token or "")
    return f"{'*' * max(len(text) - 4, 0)}{text[-4:]}" if text else None
