import base64

from django.test import SimpleTestCase, override_settings


KEYS = {
    "k1": base64.urlsafe_b64encode(b"1" * 32).decode("ascii"),
    "k2": base64.urlsafe_b64encode(b"2" * 32).decode("ascii"),
}
LOOKUP_KEY = base64.urlsafe_b64encode(b"L" * 32).decode("ascii")


@override_settings(
    FIELD_ENCRYPTION_CURRENT_VERSION="k2",
    FIELD_ENCRYPTION_KEYS=KEYS,
    FIELD_LOOKUP_KEY=LOOKUP_KEY,
    SECRET_KEY="must-not-protect-reversible-fields",
)
class FieldEncryptionTests(SimpleTestCase):
    def test_round_trip_is_versioned_field_bound_and_lookup_hash_is_stable(self):
        from sfpcl_credit.shared.encryption import FieldEncryption, InvalidCiphertext

        encrypted = FieldEncryption.encrypt("cdsl.pledgor_bo_account", "1234567890123456")

        self.assertTrue(encrypted.startswith("field:v1:k2:"))
        self.assertNotIn("1234567890123456", encrypted)
        self.assertEqual(
            FieldEncryption.decrypt("cdsl.pledgor_bo_account", encrypted),
            "1234567890123456",
        )
        self.assertEqual(FieldEncryption.mask(encrypted, 16), "************3456")
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

    def test_tamper_wrong_key_and_inactive_version_fail_closed(self):
        from sfpcl_credit.shared.encryption import (
            FieldEncryption,
            InvalidCiphertext,
        )

        encrypted = FieldEncryption.encrypt("cdsl.pledgor_bo_account", "1234567890123456")
        replacement = "A" if encrypted[-1] != "A" else "B"
        with self.assertRaises(InvalidCiphertext):
            FieldEncryption.decrypt(
                "cdsl.pledgor_bo_account", encrypted[:-1] + replacement
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
