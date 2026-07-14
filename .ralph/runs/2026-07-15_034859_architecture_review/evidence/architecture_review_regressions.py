import base64

from django.test import SimpleTestCase, override_settings
from django.utils import timezone

from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.legal_documents.models import ChecklistItem
from sfpcl_credit.security_instruments.models import BlankDatedCheque
from sfpcl_credit.tests.test_final_documentation_approval_api import (
    FinalDocumentationApprovalApiTests,
)


KEYS = {
    "k1": base64.urlsafe_b64encode(b"1" * 32).decode("ascii"),
    "k2": base64.urlsafe_b64encode(b"2" * 32).decode("ascii"),
}


@override_settings(
    FIELD_ENCRYPTION_CURRENT_VERSION="k2",
    FIELD_ENCRYPTION_KEYS=KEYS,
    FIELD_LOOKUP_KEY=base64.urlsafe_b64encode(b"L" * 32).decode("ascii"),
)
class ArchitectureReviewEncryptionRegression(SimpleTestCase):
    def test_ciphertext_does_not_embed_recoverable_plaintext_suffix(self):
        from sfpcl_credit.shared.encryption import FieldEncryption

        ciphertext = FieldEncryption.encrypt(
            "blank_cheque.cheque_number", "123456"
        )

        self.assertNotIn("3456", ciphertext)


class ArchitectureReviewChecklistRegression(FinalDocumentationApprovalApiTests):
    def test_approval_rejects_completed_rows_without_completion_actions(self):
        self.checklist.items.filter(
            applicable_flag=True,
            required_flag=True,
        ).update(
            completion_status=ChecklistItem.STATUS_COMPLETE,
            verified_by_user=self.compliance,
        )

        response = self._post_stage(
            "approve-as-company-secretary",
            self.cs,
            {"comments": "All documents verified and attached."},
        )

        self.assertEqual(response.status_code, 409, response.json())
        self.assertEqual(response.json()["error"]["code"], "EVIDENCE_BLOCKED")

    def test_cheque_completion_rejects_unbound_synthetic_ledger(self):
        self.assertFalse(
            BlankDatedCheque.objects.filter(
                security_package__loan_application=self.application
            ).exists()
        )
        VersionHistory.objects.create(
            versioned_entity_type="blank_dated_cheque",
            versioned_entity_id="10000000-0000-0000-0000-000000000088",
            version_number="1",
            change_summary="unbound synthetic ledger",
            author_user=self.compliance,
            old_value_json={},
            new_value_json={
                "loan_application_id": str(self.application.pk),
                "security_package_id": "10000000-0000-0000-0000-000000000081",
                "cheque_number": "******",
                "cheque_status": "held",
                "prepared_by_user_id": str(self.compliance.pk),
                "custodian_user_id": str(self.cs.pk),
                "custody_workflow_event_id": "10000000-0000-0000-0000-000000000082",
                "cancelled_cheque": {"verification_status": "verified"},
            },
            effective_from=timezone.localdate(),
        )
        item = self.checklist.items.get(item_code="blank_dated_cheque")
        document = self._current_document("blank_dated_cheque")

        response = self.client.post(
            f"/api/v1/checklist-items/{item.pk}/complete/",
            {"loan_document_id": str(document.pk), "remarks": None},
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )

        self.assertEqual(response.status_code, 409, response.json())
        self.assertEqual(response.json()["error"]["code"], "EVIDENCE_BLOCKED")
