"""Executable review-only probes for slices 008M5, 009B3A/B, and 009D2."""

from uuid import uuid4

from django.test import TestCase

from sfpcl_credit.domain_errors import DomainPermissionDenied
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.legal_documents.models import (
    StaffDocumentReviewAction,
)
from sfpcl_credit.legal_documents.modules import documentation_actions
from sfpcl_credit.loans.modules.loan_account_lifecycle import (
    resolve_readiness_account,
)
from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
    get_customer_code_for_member,
)
class ArchitectureReviewContractProbes(TestCase):
    def _readiness_fixture(self):
        from sfpcl_credit.tests.test_disbursement_readiness_api import (
            DisbursementReadinessApiTests,
        )

        fixture = DisbursementReadinessApiTests(
            "test_incomplete_sources_return_every_ordered_safe_blocker_without_writes"
        )
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        return fixture

    def _documentation_fixture(self, method_name):
        from sfpcl_credit.tests.test_final_documentation_approval_api import (
            FinalDocumentationApprovalApiTests,
        )

        fixture = FinalDocumentationApprovalApiTests(method_name)
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        return fixture

    def _sap_fixture(self):
        from sfpcl_credit.tests.test_sap_customer_profile_request_api import (
            SapCustomerProfileRequestApiTests,
        )

        fixture = SapCustomerProfileRequestApiTests(
            "test_client_cannot_substitute_canonical_fields"
        )
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        return fixture

    def test_009d2_preserves_source_read_roles(self):
        fixture = self._readiness_fixture()
        for role_code in ("credit_manager", "cfo", "internal_auditor"):
            with self.subTest(role_code=role_code):
                actor = fixture.fixture._user(role_code, f"Review {role_code}")
                fixture.fixture._grant(actor, "finance.disbursement.readiness")
                try:
                    resolve_readiness_account(
                        actor=actor,
                        loan_account_id=fixture.account_id,
                    )
                except DomainPermissionDenied as exc:
                    self.fail(
                        f"source-authorised readiness reader {role_code} is hard-rejected: {exc}"
                    )

    def test_009d2_approvals_fail_when_current_completion_evidence_changes(self):
        from sfpcl_credit.configurations.models import VersionHistory
        from sfpcl_credit.processes.document_checklist_actions import (
            resolve_disbursement_readiness,
        )

        fixture = self._documentation_fixture(
            "test_disbursement_readiness_reconciles_real_owner_evidence"
        )
        fixture._complete_readiness_documentation()
        item = fixture.checklist.items.get(item_code="final_checklist")
        history = VersionHistory.objects.get(
            versioned_entity_type="checklist_item_completion",
            versioned_entity_id=item.pk,
        )
        changed = dict(history.new_value_json)
        changed["request_id"] = "architecture-review-tamper"
        VersionHistory.objects.filter(pk=history.pk).update(new_value_json=changed)

        facts = resolve_disbursement_readiness(application_id=fixture.application.pk)
        self.assertFalse(facts.documentation_complete)
        self.assertFalse(
            facts.company_secretary_approval,
            "an approval must not survive changed current completion evidence",
        )
        self.assertFalse(facts.credit_manager_approval)
        self.assertFalse(facts.sanction_committee_approval)

    def test_009d2_sap_decision_reconciles_full_send_evidence(self):
        fixture = self._sap_fixture()
        request_id = fixture._create_and_send("architecture-review-sap-evidence")
        completed = fixture._complete(
            request_id, sap_customer_code="ARCH-REVIEW-SAP-001"
        )
        self.assertEqual(completed.status_code, 200, completed.content)
        send_audit = AuditLog.objects.get(
            entity_type="sap_customer_profile_request",
            entity_id=request_id,
            action="finance.sap_customer_code.sent",
        )
        changed = dict(send_audit.new_value_json)
        changed["assigned_to_user_id"] = str(uuid4())
        AuditLog.objects.filter(pk=send_audit.pk).update(new_value_json=changed)

        self.assertIsNone(
            get_customer_code_for_member(fixture.application.member_id),
            "changed retained send evidence must invalidate the current SAP decision",
        )

    def test_008m5_changed_signed_file_cannot_resolve_correction(self):
        from sfpcl_credit.documents.models import DocumentFile

        fixture = self._documentation_fixture(
            "test_staff_workspace_upload_and_correction_are_durable_owner_truth"
        )
        fixture.test_staff_workspace_upload_and_correction_are_durable_owner_truth()
        review = StaffDocumentReviewAction.objects.get(
            action_type=StaffDocumentReviewAction.TYPE_REQUEST_CORRECTION
        )
        successor = review.resolved_by_signed_copy
        DocumentFile.objects.filter(pk=successor.document_id).update(
            checksum_sha256="0" * 64
        )

        self.assertTrue(
            documentation_actions.has_open_blocker(
                review.document_checklist, review.checklist_item
            ),
            "a corrected copy with changed file evidence must fail closed",
        )
