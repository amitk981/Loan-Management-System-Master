import base64
import hashlib
import hmac
import secrets

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.conf import settings


class EncryptionConfigurationError(RuntimeError):
    pass


class InvalidCiphertext(ValueError):
    pass


class FieldEncryption:
    FORMAT = "v1"
    NONCE_BYTES = 12

    @classmethod
    def encrypt(cls, field_name: str, value: str) -> str:
        cls._validate_input(field_name, value)
        key_version = cls._current_version()
        key = cls._key(key_version)
        nonce = secrets.token_bytes(cls.NONCE_BYTES)
        length = len(value)
        last4 = value[-4:]
        header = cls._header(field_name, key_version, length, last4)
        ciphertext = AESGCM(key).encrypt(nonce, value.encode("utf-8"), header)
        return ":".join(
            (
                "field",
                cls.FORMAT,
                key_version,
                str(length),
                last4,
                cls._b64(nonce),
                cls._b64(ciphertext),
            )
        )

    @classmethod
    def decrypt(cls, field_name: str, encrypted_value: str) -> str:
        key_version, length, last4, nonce, ciphertext = cls._parse(encrypted_value)
        allowed_versions = {
            cls._current_version(),
            *getattr(settings, "FIELD_ENCRYPTION_PREVIOUS_VERSIONS", []),
        }
        if key_version not in allowed_versions:
            raise InvalidCiphertext("Ciphertext key version is not active.")
        header = cls._header(field_name, key_version, length, last4)
        try:
            plaintext = AESGCM(cls._key(key_version)).decrypt(
                nonce, ciphertext, header
            ).decode("utf-8")
        except (InvalidTag, UnicodeDecodeError) as exc:
            raise InvalidCiphertext("Ciphertext authentication failed.") from exc
        if len(plaintext) != length or plaintext[-4:] != last4:
            raise InvalidCiphertext("Ciphertext metadata is inconsistent.")
        return plaintext

    @classmethod
    def hash_for_lookup(cls, field_name: str, value: str) -> str:
        cls._validate_input(field_name, value)
        key = cls._decode_key(getattr(settings, "FIELD_LOOKUP_KEY", None), "lookup")
        message = field_name.encode("utf-8") + b"\x00" + value.encode("utf-8")
        return hmac.new(key, message, hashlib.sha256).hexdigest()

    @classmethod
    def mask(cls, encrypted_value: str | None, default_length: int) -> str | None:
        if encrypted_value is None:
            return None
        _version, length, last4, _nonce, _ciphertext = cls._parse(encrypted_value)
        length = length if length >= 4 else default_length
        return f"{'*' * max(length - 4, 0)}{last4}"

    @classmethod
    def key_version(cls, encrypted_value: str) -> str:
        return cls._parse(encrypted_value)[0]

    @classmethod
    def _current_version(cls) -> str:
        version = getattr(settings, "FIELD_ENCRYPTION_CURRENT_VERSION", None)
        if not isinstance(version, str) or not version or ":" in version:
            raise EncryptionConfigurationError(
                "FIELD_ENCRYPTION_CURRENT_VERSION is missing or invalid."
            )
        return version

    @classmethod
    def _key(cls, version: str) -> bytes:
        keys = getattr(settings, "FIELD_ENCRYPTION_KEYS", None)
        if not isinstance(keys, dict) or version not in keys:
            raise EncryptionConfigurationError(
                f"Field-encryption key version {version!r} is unavailable."
            )
        return cls._decode_key(keys[version], version)

    @staticmethod
    def _decode_key(value, label: str) -> bytes:
        if not isinstance(value, str):
            raise EncryptionConfigurationError(
                f"Field-encryption {label!r} key is missing."
            )
        try:
            decoded = base64.urlsafe_b64decode(value.encode("ascii"))
        except (ValueError, UnicodeEncodeError) as exc:
            raise EncryptionConfigurationError(
                f"Field-encryption {label!r} key is malformed."
            ) from exc
        if len(decoded) != 32:
            raise EncryptionConfigurationError(
                f"Field-encryption {label!r} key must decode to 32 bytes."
            )
        return decoded

    @classmethod
    def _parse(cls, token: str):
        parts = str(token or "").split(":")
        if len(parts) != 7 or parts[:2] != ["field", cls.FORMAT]:
            raise InvalidCiphertext("Ciphertext format or version is unsupported.")
        try:
            length = int(parts[3])
            nonce = cls._unb64(parts[5])
            ciphertext = cls._unb64(parts[6])
        except (TypeError, ValueError) as exc:
            raise InvalidCiphertext("Ciphertext is malformed.") from exc
        if length < 1 or len(parts[4]) > min(4, length) or len(nonce) != cls.NONCE_BYTES:
            raise InvalidCiphertext("Ciphertext metadata is malformed.")
        return parts[2], length, parts[4], nonce, ciphertext

    @staticmethod
    def _validate_input(field_name: str, value: str):
        if not isinstance(field_name, str) or not field_name or ":" in field_name:
            raise ValueError("A valid field name is required.")
        if not isinstance(value, str) or not value:
            raise ValueError("A non-empty string value is required.")

    @classmethod
    def _header(cls, field_name: str, key_version: str, length: int, last4: str):
        return (
            f"field:{cls.FORMAT}:{key_version}:{field_name}:{length}:{last4}"
        ).encode("utf-8")

    @staticmethod
    def _b64(value: bytes) -> str:
        return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")

    @staticmethod
    def _unb64(value: str) -> bytes:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
