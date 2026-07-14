import hashlib
import hmac
import base64
import secrets

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


def sealed_protected_identity_token(value, expected_length):
    if not isinstance(value, str) or len(value) != expected_length:
        raise ValueError("Protected identity has an unexpected length.")
    nonce = secrets.token_bytes(16)
    plaintext = value.encode("utf-8")
    encryption_key = _derived_key(b"protected-identity-seal-encryption-v1")
    authentication_key = _derived_key(b"protected-identity-seal-authentication-v1")
    ciphertext = _xor_bytes(plaintext, _keystream(encryption_key, nonce, len(plaintext)))
    header = b"seal:v1:" + str(expected_length).encode("ascii") + b":" + nonce
    tag = hmac.new(authentication_key, header + ciphertext, hashlib.sha256).digest()
    return ":".join((
        "seal", "v1", str(expected_length), _b64(nonce), _b64(ciphertext),
        _b64(tag), value[-4:],
    ))


def reveal_sealed_protected_identity(token):
    parts = str(token or "").split(":")
    if len(parts) != 7 or parts[:2] != ["seal", "v1"]:
        raise ValueError("Protected identity token is not revealable.")
    try:
        expected_length = int(parts[2])
        nonce, ciphertext, supplied_tag = map(_unb64, parts[3:6])
    except (TypeError, ValueError) as exc:
        raise ValueError("Protected identity token is malformed.") from exc
    if len(nonce) != 16:
        raise ValueError("Protected identity token is malformed.")
    encryption_key = _derived_key(b"protected-identity-seal-encryption-v1")
    authentication_key = _derived_key(b"protected-identity-seal-authentication-v1")
    header = b"seal:v1:" + str(expected_length).encode("ascii") + b":" + nonce
    expected_tag = hmac.new(
        authentication_key, header + ciphertext, hashlib.sha256
    ).digest()
    if not hmac.compare_digest(supplied_tag, expected_tag):
        raise ValueError("Protected identity token authentication failed.")
    try:
        value = _xor_bytes(
            ciphertext, _keystream(encryption_key, nonce, len(ciphertext))
        ).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Protected identity token is malformed.") from exc
    if len(value) != expected_length or value[-4:] != parts[6]:
        raise ValueError("Protected identity token is inconsistent.")
    return value


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


def _derived_key(context):
    return hmac.new(settings.SECRET_KEY.encode("utf-8"), context, hashlib.sha256).digest()


def _keystream(key, nonce, length):
    output = bytearray()
    counter = 0
    while len(output) < length:
        output.extend(hmac.new(
            key, nonce + counter.to_bytes(4, "big"), hashlib.sha256
        ).digest())
        counter += 1
    return bytes(output[:length])


def _xor_bytes(left, right):
    return bytes(a ^ b for a, b in zip(left, right, strict=True))


def _b64(value):
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _unb64(value):
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
