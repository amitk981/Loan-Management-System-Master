"""Executable review-only regressions copied from /tmp; not production tests."""

from sfpcl_credit.legal_documents.models import StaffSignedDocumentCopy
from sfpcl_credit.legal_documents.modules import documentation_actions
from sfpcl_credit.tests.test_disbursement_readiness_api import (
    DisbursementReadinessApiTests,
)
from sfpcl_credit.tests.test_final_documentation_approval_api import (
    FinalDocumentationApprovalApiTests,
)


class ArchitectureReviewDocumentationProbes(FinalDocumentationApprovalApiTests):
    def test_new_nonresolving_tail_must_reopen_the_old_correction(self):
        self._grant(
            self.compliance,
            "documents.checklist.read",
            "documents.file.upload",
        )
        self._current_document("term_sheet")
        first = self._upload_workspace_signed_copy(
            "term_sheet", "initial.pdf", b"initial", "Initial signed copy."
        )
        self.assertEqual(first.status_code, 200, first.content)

        item = next(
            row
            for row in self._workspace(self.compliance).json()["data"]["items"]
            if row["item_code"] == "term_sheet"
        )
        correction = next(
            action
            for action in item["available_actions"]
            if action["action_code"] == "request_correction"
        )
        requested = self.client.post(
            correction["action_url"],
            {"remarks": "Replace the signed copy."},
            content_type="application/json",
            **self.fixture._auth(self.compliance),
        )
        self.assertEqual(requested.status_code, 200, requested.content)

        corrected = self._upload_workspace_signed_copy(
            "term_sheet", "corrected.pdf", b"corrected", "Correction supplied."
        )
        self.assertEqual(corrected.status_code, 200, corrected.content)
        corrected_row = StaffSignedDocumentCopy.objects.get(
            pk=corrected.json()["data"]["signed_copy_id"]
        )
        self.assertIsNotNone(corrected_row.resolves_review_action_id)

        later = self._upload_workspace_signed_copy(
            "term_sheet",
            "later.pdf",
            b"later ordinary upload",
            "Later ordinary signed copy.",
        )
        self.assertEqual(later.status_code, 200, later.content)
        later_row = StaffSignedDocumentCopy.objects.get(
            pk=later.json()["data"]["signed_copy_id"]
        )
        self.assertIsNone(later_row.resolves_review_action_id)
        checklist_item = self.checklist.items.get(item_code="term_sheet")

        self.assertTrue(
            documentation_actions.has_open_blocker(self.checklist, checklist_item)
        )

    def test_unrelated_signature_history_must_not_poison_readiness(self):
        self._complete_readiness_documentation()
        self.assertTrue(self._legal_readiness().signature_mismatch_resolved)
        unrelated = self.checklist.items.get(item_code="final_checklist").loan_document
        self._signature(unrelated, "borrower")

        self.assertTrue(self._legal_readiness().signature_mismatch_resolved)


class ArchitectureReviewRoleProbe(DisbursementReadinessApiTests):
    def test_governed_cfo_authority_is_a_source_readiness_role(self):
        reader = self.fixture._user("field_officer", "Governed CFO Reader")
        reader.approval_authority_type = "cfo"
        reader.save(update_fields=["approval_authority_type"])
        self.fixture._grant(reader, "finance.disbursement.readiness")

        response = self.client.get(
            f"/api/v1/loan-accounts/{self.account_id}/disbursement-readiness/",
            **self._auth_for(reader),
        )

        self.assertEqual(response.status_code, 200, response.content)
