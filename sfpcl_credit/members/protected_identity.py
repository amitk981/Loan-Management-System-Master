from sfpcl_credit.shared.encryption import FieldEncryption, InvalidCiphertext


def identity_hash(value):
    return FieldEncryption.hash_for_lookup("identity.lookup", value)


def protected_identity_token(value, expected_length):
    return FieldEncryption.encrypt(_identity_field(expected_length), value)


def mask_protected_identity(token, default_length):
    if str(token or "").startswith("field:"):
        value = reveal_protected_identity(token, default_length)
        return f"{'*' * max(len(value) - 4, 0)}{value[-4:]}"
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


def reveal_protected_identity(token, expected_length):
    if str(token or "").startswith("field:"):
        context = _identity_field(expected_length)
        try:
            return FieldEncryption.decrypt(context, token)
        except InvalidCiphertext:
            legacy_context = "members.pan" if expected_length == 10 else "members.aadhaar"
            return FieldEncryption.decrypt(legacy_context, token)
    if str(token or "").startswith(("enc:v1:", "seal:v1:")):
        raise ValueError("The retained identity token has no reversible source value.")
    return str(token)


def _identity_field(expected_length):
    if expected_length == 10:
        return "identity.pan"
    if expected_length == 12:
        return "identity.aadhaar"
    raise ValueError("Sensitive identity length is unsupported.")
