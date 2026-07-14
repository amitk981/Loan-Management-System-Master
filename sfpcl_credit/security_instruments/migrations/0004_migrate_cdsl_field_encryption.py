import base64
import hashlib
import hmac
import secrets

from django.conf import settings
from django.db import migrations


def _b64(value):
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _unb64(value):
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _legacy_key(context):
    return hmac.new(settings.SECRET_KEY.encode("utf-8"), context, hashlib.sha256).digest()


def _legacy_hash(value):
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"), value.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def _legacy_keystream(key, nonce, length):
    output = bytearray()
    counter = 0
    while len(output) < length:
        output.extend(
            hmac.new(
                key, nonce + counter.to_bytes(4, "big"), hashlib.sha256
            ).digest()
        )
        counter += 1
    return bytes(output[:length])


def _xor(left, right):
    return bytes(a ^ b for a, b in zip(left, right, strict=True))


def _legacy_decrypt(token):
    parts = str(token or "").split(":")
    if len(parts) != 7 or parts[:2] != ["seal", "v1"]:
        raise RuntimeError("Retained CDSL ciphertext has an unsupported legacy format.")
    try:
        length = int(parts[2])
        nonce, ciphertext, supplied_tag = map(_unb64, parts[3:6])
    except (TypeError, ValueError) as exc:
        raise RuntimeError("Retained CDSL ciphertext is malformed.") from exc
    header = b"seal:v1:" + str(length).encode("ascii") + b":" + nonce
    expected_tag = hmac.new(
        _legacy_key(b"protected-identity-seal-authentication-v1"),
        header + ciphertext,
        hashlib.sha256,
    ).digest()
    if not hmac.compare_digest(supplied_tag, expected_tag):
        raise RuntimeError("Retained CDSL ciphertext failed authentication.")
    value = _xor(
        ciphertext,
        _legacy_keystream(
            _legacy_key(b"protected-identity-seal-encryption-v1"),
            nonce,
            len(ciphertext),
        ),
    ).decode("utf-8")
    if len(value) != length or value[-4:] != parts[6]:
        raise RuntimeError("Retained CDSL ciphertext failed last-four reconciliation.")
    return value


def _legacy_encrypt(value):
    nonce = secrets.token_bytes(16)
    plaintext = value.encode("utf-8")
    ciphertext = _xor(
        plaintext,
        _legacy_keystream(
            _legacy_key(b"protected-identity-seal-encryption-v1"),
            nonce,
            len(plaintext),
        ),
    )
    header = b"seal:v1:" + str(len(value)).encode("ascii") + b":" + nonce
    tag = hmac.new(
        _legacy_key(b"protected-identity-seal-authentication-v1"),
        header + ciphertext,
        hashlib.sha256,
    ).digest()
    return ":".join(
        ("seal", "v1", str(len(value)), _b64(nonce), _b64(ciphertext), _b64(tag), value[-4:])
    )


def migrate_forward(apps, schema_editor):
    from sfpcl_credit.shared.encryption import FieldEncryption

    CDSLSharePledge = apps.get_model("security_instruments", "CDSLSharePledge")
    rows = list(CDSLSharePledge.objects.all().order_by("cdsl_share_pledge_id"))
    expected_values = sum(
        1 + (row.pledgee_bo_account_encrypted is not None) for row in rows
    )
    migrated_values = 0
    for row in rows:
        updates = []
        for encrypted_column, hash_column, field_name in (
            (
                "pledgor_bo_account_encrypted",
                "pledgor_bo_account_hash",
                "cdsl.pledgor_bo_account",
            ),
            (
                "pledgee_bo_account_encrypted",
                "pledgee_bo_account_hash",
                "cdsl.pledgee_bo_account",
            ),
        ):
            token = getattr(row, encrypted_column)
            if token is None:
                continue
            if token.startswith("field:v1:"):
                value = FieldEncryption.decrypt(field_name, token)
            else:
                value = _legacy_decrypt(token)
                retained_hash = getattr(row, hash_column)
                if retained_hash != _legacy_hash(value):
                    raise RuntimeError("Retained CDSL lookup hash reconciliation failed.")
                setattr(row, encrypted_column, FieldEncryption.encrypt(field_name, value))
                setattr(row, hash_column, FieldEncryption.hash_for_lookup(field_name, value))
                updates.extend((encrypted_column, hash_column))
            if FieldEncryption.mask(getattr(row, encrypted_column), len(value))[-4:] != value[-4:]:
                raise RuntimeError("Migrated CDSL last-four reconciliation failed.")
            if getattr(row, hash_column) != FieldEncryption.hash_for_lookup(field_name, value):
                raise RuntimeError("Migrated CDSL lookup hash reconciliation failed.")
            migrated_values += 1
        if updates:
            row.save(update_fields=updates)
    if migrated_values != expected_values:
        raise RuntimeError("CDSL field-encryption row-count reconciliation failed.")


def migrate_backward(apps, schema_editor):
    from sfpcl_credit.shared.encryption import FieldEncryption

    CDSLSharePledge = apps.get_model("security_instruments", "CDSLSharePledge")
    for row in CDSLSharePledge.objects.all().order_by("cdsl_share_pledge_id"):
        updates = []
        for encrypted_column, hash_column, field_name in (
            ("pledgor_bo_account_encrypted", "pledgor_bo_account_hash", "cdsl.pledgor_bo_account"),
            ("pledgee_bo_account_encrypted", "pledgee_bo_account_hash", "cdsl.pledgee_bo_account"),
        ):
            token = getattr(row, encrypted_column)
            if token is None or token.startswith("seal:v1:"):
                continue
            value = FieldEncryption.decrypt(field_name, token)
            setattr(row, encrypted_column, _legacy_encrypt(value))
            setattr(row, hash_column, _legacy_hash(value))
            updates.extend((encrypted_column, hash_column))
        if updates:
            row.save(update_fields=updates)


class Migration(migrations.Migration):
    dependencies = [("security_instruments", "0003_cdslsharepledge_and_more")]

    operations = [migrations.RunPython(migrate_forward, migrate_backward)]
