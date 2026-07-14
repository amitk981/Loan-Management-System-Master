"""Re-encrypt retained suffix-bearing field:v1 tokens without production imports."""

import base64
import hashlib
import hmac
import secrets

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.conf import settings
from django.db import migrations, models


NONCE_BYTES = 12
TAG_BYTES = 16


def _b64(value):
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _unb64(value):
    decoded = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    if _b64(decoded) != value:
        raise RuntimeError("Retained field ciphertext has non-canonical encoding.")
    return decoded


def _key(version):
    configured = getattr(settings, "FIELD_ENCRYPTION_KEYS", {})
    try:
        decoded = base64.urlsafe_b64decode(configured[version].encode("ascii"))
    except (KeyError, TypeError, ValueError, UnicodeEncodeError) as exc:
        raise RuntimeError("Retained field-encryption key is unavailable.") from exc
    if len(decoded) != 32:
        raise RuntimeError("Retained field-encryption key is invalid.")
    return decoded


def _lookup_hash(field_name, value):
    try:
        key = base64.urlsafe_b64decode(settings.FIELD_LOOKUP_KEY.encode("ascii"))
    except (AttributeError, TypeError, ValueError, UnicodeEncodeError) as exc:
        raise RuntimeError("Field lookup key is unavailable.") from exc
    if len(key) != 32:
        raise RuntimeError("Field lookup key is invalid.")
    message = field_name.encode("utf-8") + b"\x00" + value.encode("utf-8")
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def _decrypt_v1(field_name, token):
    parts = str(token or "").split(":")
    if len(parts) != 7 or parts[:2] != ["field", "v1"]:
        raise RuntimeError("Retained suffix-bearing ciphertext is malformed.")
    try:
        length = int(parts[3])
        nonce = _unb64(parts[5])
        ciphertext = _unb64(parts[6])
    except (TypeError, ValueError) as exc:
        raise RuntimeError("Retained suffix-bearing ciphertext is malformed.") from exc
    header = f"field:v1:{parts[2]}:{field_name}:{length}:{parts[4]}".encode()
    try:
        value = AESGCM(_key(parts[2])).decrypt(nonce, ciphertext, header).decode()
    except (InvalidTag, UnicodeDecodeError) as exc:
        raise RuntimeError("Retained suffix-bearing ciphertext failed authentication.") from exc
    if len(value) != length or value[-4:] != parts[4]:
        raise RuntimeError("Retained suffix-bearing ciphertext failed reconciliation.")
    return value


def _encrypt_v1(field_name, value):
    """Frozen helper used by migration reconciliation tests for retained v1 rows."""
    version = settings.FIELD_ENCRYPTION_CURRENT_VERSION
    nonce = secrets.token_bytes(NONCE_BYTES)
    header = f"field:v1:{version}:{field_name}:{len(value)}:{value[-4:]}".encode()
    ciphertext = AESGCM(_key(version)).encrypt(nonce, value.encode(), header)
    return ":".join(
        ("field", "v1", version, str(len(value)), value[-4:], _b64(nonce), _b64(ciphertext))
    )


def _encrypt_v2(field_name, value):
    version = settings.FIELD_ENCRYPTION_CURRENT_VERSION
    plaintext = value.encode("utf-8")
    nonce = secrets.token_bytes(NONCE_BYTES)
    header = f"field:v2:{version}:{field_name}:{len(plaintext)}".encode()
    ciphertext = AESGCM(_key(version)).encrypt(nonce, plaintext, header)
    return ":".join(
        ("field", "v2", version, _b64(nonce), _b64(ciphertext))
    )


def _decrypt_v2(field_name, token):
    parts = str(token or "").split(":")
    if len(parts) != 5 or parts[:2] != ["field", "v2"]:
        raise RuntimeError("Retained opaque ciphertext is malformed.")
    nonce, ciphertext = _unb64(parts[3]), _unb64(parts[4])
    length = len(ciphertext) - TAG_BYTES
    header = f"field:v2:{parts[2]}:{field_name}:{length}".encode()
    try:
        value = AESGCM(_key(parts[2])).decrypt(nonce, ciphertext, header).decode()
    except (InvalidTag, UnicodeDecodeError) as exc:
        raise RuntimeError("Retained opaque ciphertext failed authentication.") from exc
    if len(value.encode()) != length:
        raise RuntimeError("Retained opaque ciphertext failed reconciliation.")
    return value


def _reconcile_row(row, fields):
    updates = []
    count = 0
    for encrypted_column, hash_column, field_name, suffix_column in fields:
        token = getattr(row, encrypted_column)
        if token is None:
            continue
        value = _decrypt_v2(field_name, token) if token.startswith("field:v2:") else _decrypt_v1(field_name, token)
        if getattr(row, hash_column) != _lookup_hash(field_name, value):
            raise RuntimeError("Retained lookup hash reconciliation failed.")
        if not token.startswith("field:v2:"):
            token = _encrypt_v2(field_name, value)
            setattr(row, encrypted_column, token)
            updates.append(encrypted_column)
        if suffix_column and getattr(row, suffix_column) != value[-4:]:
            setattr(row, suffix_column, value[-4:])
            updates.append(suffix_column)
        metadata_parts = token.split(":")[:3]
        if value in metadata_parts or value[-4:] in metadata_parts or str(len(value)) in metadata_parts:
            raise RuntimeError("Opaque ciphertext retains recoverable plaintext metadata.")
        count += 1
    if updates:
        row.save(update_fields=updates)
    return count


def migrate_forward(apps, schema_editor):
    CDSLSharePledge = apps.get_model("security_instruments", "CDSLSharePledge")
    BlankDatedCheque = apps.get_model("security_instruments", "BlankDatedCheque")
    expected = 0
    reconciled = 0
    for row in CDSLSharePledge.objects.all().order_by("cdsl_share_pledge_id"):
        fields = (
            ("pledgor_bo_account_encrypted", "pledgor_bo_account_hash", "cdsl.pledgor_bo_account", "pledgor_bo_account_last4"),
            ("pledgee_bo_account_encrypted", "pledgee_bo_account_hash", "cdsl.pledgee_bo_account", "pledgee_bo_account_last4"),
        )
        expected += sum(getattr(row, field[0]) is not None for field in fields)
        reconciled += _reconcile_row(row, fields)
    for row in BlankDatedCheque.objects.all().order_by("blank_dated_cheque_id"):
        fields = (("cheque_number_encrypted", "cheque_number_hash", "blank_cheque.cheque_number", None),)
        expected += 1
        reconciled += _reconcile_row(row, fields)
    if reconciled != expected:
        raise RuntimeError("Opaque field-token row-count reconciliation failed.")


class Migration(migrations.Migration):
    dependencies = [("security_instruments", "0005_blankdatedcheque_and_more")]
    operations = [
        migrations.AddField(
            model_name="cdslsharepledge",
            name="pledgor_bo_account_last4",
            field=models.CharField(default="0000", max_length=4),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="cdslsharepledge",
            name="pledgee_bo_account_last4",
            field=models.CharField(blank=True, max_length=4, null=True),
        ),
        migrations.RunPython(migrate_forward, migrations.RunPython.noop),
    ]
