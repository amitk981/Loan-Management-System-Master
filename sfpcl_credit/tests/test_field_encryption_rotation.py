import base64
from io import StringIO
import uuid

from django.apps import apps
from django.core.management import call_command
from django.test import TestCase, override_settings

from sfpcl_credit.members.models import Member
from sfpcl_credit.members.protected_identity import identity_hash, protected_identity_token
from sfpcl_credit.shared.encryption import FieldEncryption
from sfpcl_credit.shared.field_registry import FIELD_ENCRYPTION_MODELS


KEYS = {
    "k1": base64.urlsafe_b64encode(b"1" * 32).decode("ascii"),
    "k2": base64.urlsafe_b64encode(b"2" * 32).decode("ascii"),
}
LOOKUP_KEY = base64.urlsafe_b64encode(b"L" * 32).decode("ascii")


@override_settings(
    FIELD_ENCRYPTION_CURRENT_VERSION="k2",
    FIELD_ENCRYPTION_PREVIOUS_VERSIONS=["k1"],
    FIELD_ENCRYPTION_KEYS=KEYS,
    FIELD_LOOKUP_KEY=LOOKUP_KEY,
)
class FieldEncryptionRotationCommandTests(TestCase):
    def test_rotation_registry_covers_every_encrypted_database_column(self):
        actual = {
            (model._meta.label_lower, field.name)
            for model in apps.get_models()
            for field in model._meta.fields
            if field.name.endswith("_encrypted")
        }
        registered = {
            (spec.model_label.lower(), column.name)
            for spec in FIELD_ENCRYPTION_MODELS
            for column in spec.columns
        }

        self.assertEqual(registered, actual)

    def test_rotation_reconciles_identity_fields_and_is_safely_rerunnable(self):
        with override_settings(
            FIELD_ENCRYPTION_CURRENT_VERSION="k1",
            FIELD_ENCRYPTION_PREVIOUS_VERSIONS=[],
        ):
            member = Member.objects.create(
                member_type="individual_farmer",
                legal_name="Synthetic Rotation Member",
                display_name="Synthetic Rotation Member",
                folio_number="ROTATION-001",
                membership_status="active",
                pan_encrypted=protected_identity_token("ABCDE1234F", 10),
                pan_hash=identity_hash("ABCDE1234F"),
                aadhaar_encrypted=protected_identity_token("123456789012", 12),
                aadhaar_hash=identity_hash("123456789012"),
                aadhaar_last4="9012",
                kyc_status="verified",
                default_status="no_default",
            )

        first_output = StringIO()
        call_command(
            "rotate_field_encryption",
            from_version="k1",
            stdout=first_output,
        )
        member.refresh_from_db()

        self.assertEqual(FieldEncryption.key_version(member.pan_encrypted), "k2")
        self.assertEqual(FieldEncryption.key_version(member.aadhaar_encrypted), "k2")
        self.assertEqual(
            FieldEncryption.decrypt("identity.pan", member.pan_encrypted),
            "ABCDE1234F",
        )
        self.assertIn(
            "reconciliation scanned=2 rotated=2 already_current=0 "
            "legacy_unrecoverable=0",
            first_output.getvalue(),
        )

        second_output = StringIO()
        call_command(
            "rotate_field_encryption",
            from_version="k1",
            stdout=second_output,
        )

        self.assertIn(
            "reconciliation scanned=2 rotated=0 already_current=2 "
            "legacy_unrecoverable=0",
            second_output.getvalue(),
        )

    def test_rotation_resumes_strictly_after_a_saved_cursor(self):
        with override_settings(
            FIELD_ENCRYPTION_CURRENT_VERSION="k1",
            FIELD_ENCRYPTION_PREVIOUS_VERSIONS=[],
        ):
            first = self._member(
                "ROTATION-RESUME-001",
                "ABCDE1001F",
                member_id=uuid.UUID(int=1),
            )
            second = self._member(
                "ROTATION-RESUME-002",
                "ABCDE1002F",
                member_id=uuid.UUID(int=2),
            )
        cursor = f"members.Member:{first.member_id}"
        output = StringIO()

        call_command(
            "rotate_field_encryption",
            from_version="k1",
            resume_after=cursor,
            stdout=output,
        )
        first.refresh_from_db()
        second.refresh_from_db()

        self.assertEqual(FieldEncryption.key_version(first.pan_encrypted), "k1")
        self.assertEqual(FieldEncryption.key_version(second.pan_encrypted), "k2")
        self.assertIn(f"resumed_after={cursor}", output.getvalue())
        self.assertIn(
            "reconciliation scanned=1 rotated=1 already_current=0 "
            "legacy_unrecoverable=0",
            output.getvalue(),
        )

    def test_rotation_recovers_plaintext_legacy_and_reports_one_way_tokens(self):
        member = Member.objects.create(
            member_type="individual_farmer",
            legal_name="Synthetic Legacy Member",
            display_name="Synthetic Legacy Member",
            folio_number="ROTATION-LEGACY-001",
            membership_status="active",
            pan_encrypted="ABCDE4321F",
            pan_hash="retained-secret-derived-pan-hash",
            aadhaar_encrypted="enc:v1:12:retained-one-way-token:9012",
            aadhaar_hash="retained-secret-derived-aadhaar-hash",
            aadhaar_last4="9012",
            kyc_status="verified",
            default_status="no_default",
        )
        output = StringIO()

        call_command(
            "rotate_field_encryption",
            from_version="k1",
            stdout=output,
        )
        member.refresh_from_db()

        self.assertEqual(
            FieldEncryption.decrypt("identity.pan", member.pan_encrypted),
            "ABCDE4321F",
        )
        self.assertEqual(member.pan_hash, identity_hash("ABCDE4321F"))
        self.assertEqual(
            member.aadhaar_encrypted,
            "enc:v1:12:retained-one-way-token:9012",
        )
        self.assertIn("legacy_recovered=1", output.getvalue())
        self.assertIn("legacy_unrecoverable=1", output.getvalue())

    @staticmethod
    def _member(folio_number, pan, **overrides):
        return Member.objects.create(
            member_type="individual_farmer",
            legal_name=folio_number,
            display_name=folio_number,
            folio_number=folio_number,
            membership_status="active",
            pan_encrypted=protected_identity_token(pan, 10),
            pan_hash=identity_hash(pan),
            kyc_status="verified",
            default_status="no_default",
            **overrides,
        )
