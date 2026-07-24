import base64


class FieldKeyConfigurationError(ValueError):
    pass


def validate_field_key_configuration(
    *,
    current_version,
    previous_versions,
    keys,
    lookup_key,
    key_reference,
):
    if (
        not isinstance(current_version, str)
        or not current_version
        or ":" in current_version
    ):
        raise FieldKeyConfigurationError(
            "SFPCL_FIELD_ENCRYPTION_CURRENT_VERSION is missing or invalid."
        )
    if not isinstance(previous_versions, list) or any(
        not isinstance(version, str) or not version or ":" in version
        for version in previous_versions
    ):
        raise FieldKeyConfigurationError(
            "SFPCL_FIELD_ENCRYPTION_PREVIOUS_VERSIONS is invalid."
        )
    if current_version in previous_versions or len(set(previous_versions)) != len(
        previous_versions
    ):
        raise FieldKeyConfigurationError(
            "Field-encryption current and previous versions must be distinct."
        )
    required_versions = (current_version, *previous_versions)
    if not isinstance(keys, dict):
        raise FieldKeyConfigurationError(
            "SFPCL_FIELD_ENCRYPTION_KEYS must be a JSON object."
        )
    for version in required_versions:
        if version not in keys:
            raise FieldKeyConfigurationError(
                f"SFPCL_FIELD_ENCRYPTION_KEYS is missing version {version!r}."
            )
        _decode_32_byte_key(keys[version], f"field key {version!r}")
    _decode_32_byte_key(lookup_key, "SFPCL_FIELD_LOOKUP_KEY")
    if (
        not isinstance(key_reference, str)
        or not key_reference.strip()
        or key_reference == "local-development-only"
    ):
        raise FieldKeyConfigurationError(
            "SFPCL_FIELD_ENCRYPTION_KEY_REF is missing or invalid."
        )


def _decode_32_byte_key(value, label):
    if not isinstance(value, str):
        raise FieldKeyConfigurationError(f"{label} is missing.")
    try:
        decoded = base64.urlsafe_b64decode(value.encode("ascii"))
    except (ValueError, UnicodeEncodeError) as exc:
        raise FieldKeyConfigurationError(f"{label} is malformed.") from exc
    if len(decoded) != 32:
        raise FieldKeyConfigurationError(f"{label} must decode to 32 bytes.")
    if base64.urlsafe_b64encode(decoded).decode("ascii") != value:
        raise FieldKeyConfigurationError(f"{label} is malformed.")
