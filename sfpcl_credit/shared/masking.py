"""Canonical recursive redaction for retained evidence payloads."""

import re
import uuid


SENSITIVE_KEY_PARTS = (
    "aadhaar",
    "account_number",
    "bank_account",
    "bo_account",
    "cheque_hash",
    "cheque_number",
    "pan_number",
)

SAFE_MASK_PATTERN = re.compile(r"\*+(?:[A-Za-z0-9]{1,4})?")


def redact_sensitive_mapping(value, key=""):
    if isinstance(value, dict):
        return {
            item_key: redact_sensitive_mapping(item_value, item_key)
            for item_key, item_value in value.items()
        }
    if isinstance(value, list):
        return [redact_sensitive_mapping(item, key) for item in value]
    if any(part in key.lower() for part in SENSITIVE_KEY_PARTS):
        if isinstance(value, str) and SAFE_MASK_PATTERN.fullmatch(value):
            return value
        return None if value is None else "[REDACTED]"
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    return value
