import sys
import unittest
from unittest import mock

import django
from django.test.runner import DiscoverRunner

django.setup()

from sfpcl_credit.tests.test_portal_deficiency_response_api import (
    PortalDeficiencyResponseApiTests,
)
from sfpcl_credit.tests.test_portal_documentation_actions_api import (
    PortalDocumentationActionsApiTests,
)
from sfpcl_credit.identity.models import Permission, RolePermission
from sfpcl_credit.documents.models import DocumentFile, DocumentTemplate
from sfpcl_credit.legal_documents.models import LoanDocument
from sfpcl_credit.legal_documents.modules.checklist_actions import RequestMetadata
from sfpcl_credit.processes import document_checklist_actions


class PortalDocumentationCapabilityProbe(PortalDocumentationActionsApiTests):
    def test_issued_document_content_url_is_signed_and_scope_bound(self):
        _output, loan_document = self._generated_document(
            "term_sheet", b"review probe term sheet", "review-probe-term-sheet.pdf"
        )
        item = self.checklist.items.get(item_code="term_sheet")
        item.loan_document = loan_document
        item.save(update_fields=["loan_document"])
        descriptor = self.client.get(
            f"{self._collection_url()}term_sheet/download/",
            headers=self._portal_auth(),
        )
        self.assertEqual(descriptor.status_code, 200, descriptor.content)
        content_url = descriptor.json()["data"]["download_url"]
        self.assertIn("token=", content_url)
        self.assertNotIn("expires_at=", content_url)

    def test_portal_completion_reconciles_the_current_renderer_document(self):
        permission, _ = Permission.objects.get_or_create(
            permission_code="documents.checklist.update",
            defaults={
                "permission_name": "Update documentation checklist",
                "module_name": "documents",
                "risk_level": Permission.RISK_HIGH,
            },
        )
        RolePermission.objects.get_or_create(
            role=self.fixture.actor.primary_role, permission=permission
        )
        _output, original = self._generated_document(
            "document_checklist", b"review probe original", "review-probe-original.pdf"
        )
        item = self.checklist.items.get(item_code="final_checklist")
        document_checklist_actions.complete_item(
            actor=self.fixture.actor,
            checklist_item_id=item.pk,
            payload={"loan_document_id": str(original.pk), "remarks": "Reviewed."},
            metadata=RequestMetadata(
                request_id="review-current-evidence", ip_address="127.0.0.1", user_agent="probe"
            ),
        )
        replacement_file = DocumentFile.objects.create(
            file_name="review-probe-replacement.pdf",
            file_extension=".pdf",
            mime_type="application/pdf",
            file_size_bytes=24,
            storage_provider="local",
            storage_key="generated/review-probe-replacement.pdf",
            checksum_sha256="replacement-checksum",
            uploaded_by_user=self.fixture.actor,
            sensitivity_level="confidential",
        )
        replacement_template = DocumentTemplate.objects.create(
            template_code="portal-document_checklist-v2",
            template_name="Portal document_checklist replacement",
            document_type="document_checklist",
            borrower_type="individual_farmer",
            template_version="2.0",
            merge_fields_json=[],
            approval_status="approved",
            effective_from=original.document_template.effective_from,
        )
        LoanDocument.objects.create(
            loan_application=self.application,
            document_type="document_checklist",
            document_category="legal",
            party_required="borrower",
            document_template=replacement_template,
            document=replacement_file,
            output_format="pdf",
            generation_status="generated",
            execution_status="pending",
            verification_status="verified",
            renderer_contract_version=LoanDocument.RENDERER_CONTRACT_V1,
            renderer_validated_document_id=replacement_file.pk,
            renderer_validated_checksum_sha256=replacement_file.checksum_sha256,
        )
        response = self.client.get(self._collection_url(), headers=self._portal_auth())
        self.assertEqual(response.status_code, 200, response.content)
        projected = self._action(response.json()["data"], "final_checklist")
        self.assertEqual(projected["status"], "pending_borrower")


class PortalDeficiencyLifecycleProbe(PortalDeficiencyResponseApiTests):
    def test_resubmission_crosses_the_application_transition_guard(self):
        token = self._token()
        self.assertEqual(self._upload(token).status_code, 200)
        with mock.patch(
            "sfpcl_credit.applications.services.evaluate_transition",
            wraps=__import__(
                "sfpcl_credit.applications.services", fromlist=["evaluate_transition"]
            ).evaluate_transition,
        ) as transition_guard:
            response = self.client.post(
                self._url("resubmit/"),
                data={},
                content_type="application/json",
                headers={"Authorization": f"Bearer {token}"},
            )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(
            transition_guard.called,
            "The source-defined application lifecycle guard was bypassed.",
        )


if __name__ == "__main__":
    runner = DiscoverRunner(verbosity=2, interactive=False)
    runner.setup_test_environment()
    old_config = runner.setup_databases()
    try:
        suite = unittest.TestSuite(
            [
                PortalDocumentationCapabilityProbe(
                    "test_issued_document_content_url_is_signed_and_scope_bound"
                ),
                PortalDocumentationCapabilityProbe(
                    "test_portal_completion_reconciles_the_current_renderer_document"
                ),
                PortalDeficiencyLifecycleProbe(
                    "test_resubmission_crosses_the_application_transition_guard"
                ),
            ]
        )
        failures = runner.run_suite(suite)
    finally:
        runner.teardown_databases(old_config)
        runner.teardown_test_environment()
    sys.exit(bool(failures))
