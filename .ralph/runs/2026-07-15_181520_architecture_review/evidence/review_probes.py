import sys
import unittest

import django
from django.test.runner import DiscoverRunner

django.setup()

from sfpcl_credit.applications.modules import bank_verification
from sfpcl_credit.configurations.models import VersionHistory
from sfpcl_credit.legal_documents.models import ChecklistItem
from sfpcl_credit.legal_documents.modules import checklist_actions
from sfpcl_credit.processes import document_checklist_actions
from sfpcl_credit.tests.test_final_documentation_approval_api import (
    FinalDocumentationApprovalApiTests,
)


class CurrentEvidenceReviewProbes(FinalDocumentationApprovalApiTests):
    def test_borrower_projection_rejects_changed_completion_version_body(self):
        self._complete_all_applicable_items()
        item = self.checklist.items.get(item_code="final_checklist")
        initially_complete = checklist_actions.borrower_safe_completed_item_ids(
            self.checklist,
            terminal_security_evidence=(
                document_checklist_actions._terminal_security_evidence
            ),
        )
        self.assertIn(item.pk, initially_complete)

        history = VersionHistory.objects.get(
            versioned_entity_type="checklist_item_completion",
            versioned_entity_id=item.pk,
        )
        changed = dict(history.new_value_json)
        changed["request_id"] = "tampered-after-completion"
        VersionHistory.objects.filter(pk=history.pk).update(new_value_json=changed)

        projected = checklist_actions.borrower_safe_completed_item_ids(
            self.checklist,
            terminal_security_evidence=(
                document_checklist_actions._terminal_security_evidence
            ),
        )
        self.assertNotIn(
            item.pk,
            projected,
            "Borrower-safe completion accepted a changed retained version body.",
        )

    def test_bank_decision_rejects_non_documentation_application_state(self):
        self._complete_all_applicable_items()
        self.application.refresh_from_db()
        self.application.application_status = self.application.STATUS_DRAFT
        self.application.save(update_fields=["application_status"])

        prior = self.application.bank_verification_decisions.order_by(
            "-decision_version"
        ).first()
        response = self.client.post(
            f"/api/v1/loan-applications/{self.application.pk}/bank-verification-decision/",
            {
                "bank_account_id": str(prior.bank_account_id),
                "cancelled_cheque_id": str(prior.cancelled_cheque_id),
                "decision_status": bank_verification.BankVerificationDecision.STATUS_REJECTED,
            },
            content_type="application/json",
            HTTP_X_REQUEST_ID="architecture-review-draft-bank-decision",
            **self.fixture._auth(self.compliance),
        )
        self.assertIn(
            response.status_code,
            {403, 409},
            "A draft application accepted immutable Stage-4 bank evidence.",
        )


if __name__ == "__main__":
    runner = DiscoverRunner(verbosity=2, interactive=False)
    runner.setup_test_environment()
    old_config = runner.setup_databases()
    try:
        suite = unittest.TestSuite(
            [
                CurrentEvidenceReviewProbes(
                    "test_borrower_projection_rejects_changed_completion_version_body"
                ),
                CurrentEvidenceReviewProbes(
                    "test_bank_decision_rejects_non_documentation_application_state"
                ),
            ]
        )
        failures = runner.run_suite(suite)
    finally:
        runner.teardown_databases(old_config)
        runner.teardown_test_environment()
    sys.exit(bool(failures))
