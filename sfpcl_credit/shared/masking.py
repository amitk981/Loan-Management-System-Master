"""Canonical recursive redaction for retained evidence payloads."""

import re
import uuid


SENSITIVE_KEY_PARTS = (
    "aadhaar",
    "access_token",
    "account_number",
    "authorization",
    "bank_account",
    "bo_account",
    "cheque_hash",
    "cheque_number",
    "cookie",
    "password",
    "pan_number",
    "refresh_token",
    "request_body",
    "secret",
)
SENSITIVE_EXACT_KEYS = {"pan", "token"}

SAFE_MASK_PATTERN = re.compile(r"\*+(?:[A-Za-z0-9]{1,4})?")


def redact_sensitive_mapping(value, key=""):
    if _is_sensitive_key(key):
        if isinstance(value, str) and SAFE_MASK_PATTERN.fullmatch(value):
            return value
        return None if value is None else "[REDACTED]"
    if isinstance(value, dict):
        return {
            item_key: redact_sensitive_mapping(item_value, item_key)
            for item_key, item_value in value.items()
        }
    if isinstance(value, list):
        return [redact_sensitive_mapping(item, key) for item in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    return value


def _is_sensitive_key(key):
    normalized = key.lower()
    return normalized in SENSITIVE_EXACT_KEYS or any(
        part in normalized for part in SENSITIVE_KEY_PARTS
    )
