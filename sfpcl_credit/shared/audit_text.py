import re
from collections.abc import Iterable


SAFE_AUDIT_TEXT_ERROR = "The reason contains unsafe or invalid audit text."

_FORMATTED_DIGIT_SEQUENCE = re.compile(r"(?<!\d)(?:\d[\s/.-]?){7,}\d(?!\d)")
_FIELD_TOKEN_PREFIX = re.compile(r"(?i)(?<![a-z0-9])field:v\d+:")
_LOOKUP_HASH = re.compile(r"(?i)(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])")
_LEGACY_TOKEN_MARKERS = ("enc:v", "aes-gcm", "ciphertext:")


class UnsafeAuditText(ValueError):
    pass


def safe_audit_text(
    value: object,
    *,
    max_length: int,
    protected_values: Iterable[object] = (),
) -> str:
    """Return bounded reviewable text or reject it without echoing unsafe input."""
    text = value.strip() if isinstance(value, str) else ""
    lowered = text.casefold()
    unsafe = (
        not text
        or len(text) > max_length
        or not text.isprintable()
        or bool(_FORMATTED_DIGIT_SEQUENCE.search(text))
        or bool(_FIELD_TOKEN_PREFIX.search(text))
        or bool(_LOOKUP_HASH.search(text))
        or any(marker in lowered for marker in _LEGACY_TOKEN_MARKERS)
        or any(
            isinstance(protected, str)
            and len(protected.strip()) >= 4
            and protected.strip().casefold() in lowered
            for protected in protected_values
        )
    )
    if unsafe:
        raise UnsafeAuditText(SAFE_AUDIT_TEXT_ERROR)
    return text


__all__ = (
    "SAFE_AUDIT_TEXT_ERROR",
    "UnsafeAuditText",
    "safe_audit_text",
)
