import base64
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

from django.test import SimpleTestCase, override_settings


KEYS = {
    "k1": base64.urlsafe_b64encode(b"1" * 32).decode("ascii"),
    "k2": base64.urlsafe_b64encode(b"2" * 32).decode("ascii"),
}
LOOKUP_KEY = base64.urlsafe_b64encode(b"L" * 32).decode("ascii")
REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_RUNTIME_ENVIRONMENT = {
    "SFPCL_SECRET_KEY": "synthetic-production-django-key-32",
    "SFPCL_JWT_SIGNING_KEY": "synthetic-production-jwt-key-value",
    "SFPCL_ALLOWED_HOSTS": "credit.example.test",
    "SFPCL_CORS_ORIGINS": "https://lms.example.test",
    "SFPCL_CSRF_TRUSTED_ORIGINS": "https://lms.example.test",
}


def _noncanonical_ciphertext_token(token: str) -> str:
    prefix, ciphertext = token.rsplit(":", 1)
    return f"{prefix}:{ciphertext}="


def _canonical_ciphertext_tamper(token: str) -> str:
    prefix, ciphertext = token.rsplit(":", 1)
    replacement = "A" if ciphertext[0] != "A" else "B"
    return f"{prefix}:{replacement}{ciphertext[1:]}"


@override_settings(
    FIELD_ENCRYPTION_CURRENT_VERSION="k2",
    FIELD_ENCRYPTION_KEYS=KEYS,
    FIELD_LOOKUP_KEY=LOOKUP_KEY,
    SECRET_KEY="must-not-protect-reversible-fields",
)
class FieldEncryptionTests(SimpleTestCase):
    def test_production_boot_requires_explicit_valid_dedicated_field_keys(self):
        base_env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("SFPCL_FIELD_")
        }
        base_env["DJANGO_SETTINGS_MODULE"] = (
            "sfpcl_credit.config.production_settings"
        )
        base_env.update(PRODUCTION_RUNTIME_ENVIRONMENT)

        missing = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sfpcl_credit.config.production_settings",
            ],
            cwd=REPO_ROOT,
            env=base_env,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("SFPCL_FIELD_ENCRYPTION_KEYS", missing.stderr)

        malformed = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sfpcl_credit.config.production_settings",
            ],
            cwd=REPO_ROOT,
            env={
                **base_env,
                "SFPCL_FIELD_ENCRYPTION_CURRENT_VERSION": "prod-v1",
                "SFPCL_FIELD_ENCRYPTION_KEY_REF": "vault:prod/field/prod-v1",
                "SFPCL_FIELD_ENCRYPTION_KEYS": json.dumps(
                    {
                        "prod-v1": base64.urlsafe_b64encode(b"short").decode(
                            "ascii"
                        )
                    }
                ),
                "SFPCL_FIELD_LOOKUP_KEY": LOOKUP_KEY,
            },
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(malformed.returncode, 0)
        self.assertIn("must decode to 32 bytes", malformed.stderr)

        configured = subprocess.run(
            [
                sys.executable,
                "-c",
                "import sfpcl_credit.config.production_settings",
            ],
            cwd=REPO_ROOT,
            env={
                **base_env,
                "SFPCL_FIELD_ENCRYPTION_CURRENT_VERSION": "prod-v1",
                "SFPCL_FIELD_ENCRYPTION_KEY_REF": "vault:prod/field/prod-v1",
                "SFPCL_FIELD_ENCRYPTION_KEYS": json.dumps(
                    {"prod-v1": KEYS["k1"]}
                ),
                "SFPCL_FIELD_LOOKUP_KEY": LOOKUP_KEY,
            },
            capture_output=True,
            text=True,
        )

        self.assertEqual(configured.returncode, 0, configured.stderr)

    def test_identity_tokens_and_reveal_use_dedicated_versioned_field_key(self):
        from sfpcl_credit.members.protected_identity import protected_identity_token
        from sfpcl_credit.members.services import sensitive_field_value

        token = protected_identity_token("ABCDE1234F", 10)

        self.assertTrue(token.startswith("field:v2:k2:"))
        self.assertNotIn("ABCDE1234F", token)
        with override_settings(SECRET_KEY="rotated-application-secret"):
            self.assertEqual(
                sensitive_field_value(
                    SimpleNamespace(pan_encrypted=token),
                    "pan",
                ),
                "ABCDE1234F",
            )

    def test_round_trip_is_versioned_field_bound_and_lookup_hash_is_stable(self):
        from sfpcl_credit.shared.encryption import FieldEncryption, InvalidCiphertext

        encrypted = FieldEncryption.encrypt(
            "cdsl.pledgor_bo_account", "1234567890123456"
        )

        self.assertTrue(encrypted.startswith("field:v2:k2:"))
        self.assertNotIn("1234567890123456", encrypted)
        self.assertEqual(len(encrypted.split(":")), 5)
        self.assertNotIn("3456", encrypted.split(":")[:3])
        self.assertNotIn("16", encrypted.split(":")[:3])
        self.assertEqual(
            FieldEncryption.decrypt("cdsl.pledgor_bo_account", encrypted),
            "1234567890123456",
        )
        first_hash = FieldEncryption.hash_for_lookup(
            "cdsl.pledgor_bo_account", "1234567890123456"
        )
        self.assertEqual(
            first_hash,
            FieldEncryption.hash_for_lookup(
                "cdsl.pledgor_bo_account", "1234567890123456"
            ),
        )
        self.assertNotIn("1234567890123456", first_hash)
        with self.assertRaises(InvalidCiphertext):
            FieldEncryption.decrypt("cdsl.pledgee_bo_account", encrypted)

    def test_noncanonical_base64_tamper_is_rejected_as_malformed(self):
        from sfpcl_credit.shared.encryption import FieldEncryption, InvalidCiphertext

        encrypted = FieldEncryption.encrypt(
            "cdsl.pledgor_bo_account", "1234567890123456"
        )

        with self.assertRaisesRegex(InvalidCiphertext, "Ciphertext is malformed"):
            FieldEncryption.decrypt(
                "cdsl.pledgor_bo_account",
                _noncanonical_ciphertext_token(encrypted),
            )

    def test_canonical_ciphertext_tamper_is_rejected_by_authentication(self):
        from sfpcl_credit.shared.encryption import FieldEncryption, InvalidCiphertext

        encrypted = FieldEncryption.encrypt(
            "cdsl.pledgor_bo_account", "1234567890123456"
        )

        with self.assertRaisesRegex(
            InvalidCiphertext, "Ciphertext authentication failed"
        ):
            FieldEncryption.decrypt(
                "cdsl.pledgor_bo_account",
                _canonical_ciphertext_tamper(encrypted),
            )

    def test_wrong_key_and_inactive_version_fail_closed(self):
        from sfpcl_credit.shared.encryption import (
            FieldEncryption,
            InvalidCiphertext,
        )

        encrypted = FieldEncryption.encrypt(
            "cdsl.pledgor_bo_account", "1234567890123456"
        )
        with override_settings(
            FIELD_ENCRYPTION_KEYS={**KEYS, "k2": KEYS["k1"]}
        ):
            with self.assertRaises(InvalidCiphertext):
                FieldEncryption.decrypt("cdsl.pledgor_bo_account", encrypted)
        with override_settings(
            FIELD_ENCRYPTION_CURRENT_VERSION="k1",
            FIELD_ENCRYPTION_PREVIOUS_VERSIONS=[],
        ):
            with self.assertRaises(InvalidCiphertext):
                FieldEncryption.decrypt("cdsl.pledgor_bo_account", encrypted)

    def test_previous_key_remains_readable_during_rotation(self):
        from sfpcl_credit.shared.encryption import FieldEncryption

        with override_settings(
            FIELD_ENCRYPTION_CURRENT_VERSION="k1",
            FIELD_ENCRYPTION_PREVIOUS_VERSIONS=[],
        ):
            old = FieldEncryption.encrypt(
                "cdsl.pledgor_bo_account", "1234567890123456"
            )
        with override_settings(FIELD_ENCRYPTION_PREVIOUS_VERSIONS=["k1"]):
            self.assertEqual(
                FieldEncryption.decrypt("cdsl.pledgor_bo_account", old),
                "1234567890123456",
            )

    def test_random_ciphertext_and_field_specific_hashes_do_not_expose_plaintext(self):
        from sfpcl_credit.shared.encryption import FieldEncryption

        first = FieldEncryption.encrypt("cdsl.pledgor_bo_account", "1234567890123456")
        second = FieldEncryption.encrypt("cdsl.pledgor_bo_account", "1234567890123456")
        self.assertNotEqual(first, second)
        self.assertEqual(
            FieldEncryption.hash_for_lookup(
                "cdsl.pledgor_bo_account", "1234567890123456"
            ),
            FieldEncryption.hash_for_lookup(
                "cdsl.pledgor_bo_account", "1234567890123456"
            ),
        )
        for token in (first, second):
            self.assertNotIn("1234567890123456", token)
            self.assertNotIn("3456", token.split(":")[:3])
        self.assertNotEqual(
            FieldEncryption.hash_for_lookup(
                "cdsl.pledgor_bo_account", "1234567890123456"
            ),
            FieldEncryption.hash_for_lookup(
                "cdsl.pledgee_bo_account", "1234567890123456"
            ),
        )

    def test_missing_dedicated_keys_never_fall_back_to_django_secret_key(self):
        from sfpcl_credit.shared.encryption import (
            EncryptionConfigurationError,
            FieldEncryption,
        )

        with override_settings(
            FIELD_ENCRYPTION_KEYS={},
            FIELD_LOOKUP_KEY=None,
            SECRET_KEY="changing-this-must-not-help",
        ):
            with self.assertRaises(EncryptionConfigurationError):
                FieldEncryption.encrypt(
                    "cdsl.pledgor_bo_account", "1234567890123456"
                )
            with self.assertRaises(EncryptionConfigurationError):
                FieldEncryption.hash_for_lookup(
                    "cdsl.pledgor_bo_account", "1234567890123456"
                )
