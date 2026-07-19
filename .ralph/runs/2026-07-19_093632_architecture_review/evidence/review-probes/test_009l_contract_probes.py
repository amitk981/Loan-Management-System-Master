"""Review-only probes for 009L; never imported by the product test suite."""

from django.test import Client, TestCase
from django.utils import timezone

from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
    get_account_customer_code,
    get_customer_code_for_member,
)


class CreditManagerSapWorkspaceScopeProbe(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_sap_customer_profile_request_api import (
            SapCustomerProfileRequestApiTests,
        )

        self.fixture = SapCustomerProfileRequestApiTests(
            "test_credit_manager_creates_draft_request_after_terminal_sanction"
        )
        self.fixture.setUp()
        self.other_credit_manager = self.fixture._user(
            "credit_manager",
            "Current Credit Manager Outside Intake Ownership",
            "finance.sap_request.create",
            "finance.sap_request.send",
        )
        self.client = Client()

    def tearDown(self):
        self.fixture.tearDown()

    def test_mutation_authorised_credit_manager_can_reach_s36_candidate(self):
        workspace = self.client.get(
            "/api/v1/disbursement-workspaces/",
            **self.fixture._auth(self.other_credit_manager),
        )
        mutation = self.client.post(
            (
                f"/api/v1/loan-applications/{self.fixture.application.pk}/"
                "sap-customer-profile-request/"
            ),
            {"assigned_to_user_id": str(self.fixture.assignee.pk)},
            content_type="application/json",
            **self.fixture._auth(self.other_credit_manager),
        )

        self.assertEqual(mutation.status_code, 200, mutation.content)
        self.assertEqual(workspace.status_code, 200, workspace.content)
        self.assertEqual(
            workspace.json()["pagination"]["total_count"],
            1,
            "S36 must not hide an action its public mutation owner accepts.",
        )


class SapCompletionEvidenceFacadeProbe(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_disbursement_transfer_success_api import (
            DisbursementTransferSuccessApiTests,
        )

        self.fixture = DisbursementTransferSuccessApiTests(
            "test_public_success_records_transfer_and_activates_exact_loan_atomically"
        )
        self.fixture.setUp()
        transferred = self.fixture._post(
            bank_reference_number="RBL-REVIEW-SAP-EVIDENCE",
            disbursed_at=timezone.now(),
        )
        self.assertEqual(transferred.status_code, 200, transferred.content)
        self.account = self.fixture.owner.fixture.application.loan_account
        self.account.refresh_from_db()

        audit = AuditLog.objects.get(
            action__in=("sap.customer_code_created", "sap.customer_code_reused")
        )
        changed = dict(audit.new_value_json)
        changed["completion_input_digest"] = "0" * 64
        AuditLog.objects.filter(pk=audit.pk).update(new_value_json=changed)

    def test_account_facade_rejects_drift_rejected_by_canonical_member_facade(self):
        self.assertIsNone(get_customer_code_for_member(self.account.member_id))
        self.assertIsNone(
            get_account_customer_code(
                application_id=self.account.loan_application_id,
                member_id=self.account.member_id,
                customer_code_id=self.account.sap_customer_code_id,
            ),
            "Every SAP read facade must enforce the same immutable completion evidence.",
        )


class GovernedCfcWorkspaceAuthorityProbe(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_disbursement_authorisation_api import (
            DisbursementAuthorisationApiTests,
        )

        self.fixture = DisbursementAuthorisationApiTests(
            "test_cfc_approval_is_terminal_evidence_but_not_bank_execution"
        )
        self.fixture.setUp()
        self.fixture.cfc.approval_authority_type = ""
        self.fixture.cfc.save(update_fields=["approval_authority_type"])
        self.client = Client()

    def test_primary_role_without_governed_cfc_authority_gets_no_actions(self):
        response = self.client.get(
            "/api/v1/disbursement-workspaces/",
            **self.fixture.fixture._auth(self.fixture.cfc),
        )

        self.assertEqual(response.status_code, 200, response.content)
        actions = response.json()["data"][0]["available_actions"]
        self.assertEqual(
            actions,
            [],
            "The workspace must not advertise actions rejected by the mutation owner.",
        )
