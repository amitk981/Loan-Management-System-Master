"""Review-only probes for 009L5's exact database selector contract.

Each mutation preserves the narrow predicate added by 009L5 while violating a
different invariant enforced by the public scalar owner. Exact collection
identity requires the row to affect neither total nor page contents.
"""

from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest
from sfpcl_credit.tests.test_disbursement_workspace_api import (
    DisbursementWorkspaceApiTests,
    SapStaffWorkspaceApiTests,
)
from sfpcl_credit.tests.test_loan_account_reads_api import (
    ActiveLoanAccountReadApiTests,
    LoanAccountReadApiTests,
)


class LoanAccountUntestedDriftProbe(LoanAccountReadApiTests):
    def test_creation_team_shape_drift_affects_neither_total_nor_page(self):
        audit = AuditLog.objects.get(
            action="finance.loan_account.created",
            entity_id=self.account.pk,
        )
        audit.new_value_json = {
            **audit.new_value_json,
            "actor_team_codes": "not-an-immutable-team-list",
        }
        audit.save(update_fields=["new_value_json"])

        response = self.client.get("/api/v1/loan-accounts/", **self.auth)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])


class SapCompletionUntestedDriftProbe(ActiveLoanAccountReadApiTests):
    def test_completion_body_drift_affects_neither_total_nor_page(self):
        request = SapCustomerProfileRequest.objects.get(
            loan_application_id=self.account.loan_application_id,
            request_status=SapCustomerProfileRequest.STATUS_COMPLETED,
        )
        audit = AuditLog.objects.get(
            entity_type="sap_customer_profile_request",
            entity_id=request.pk,
            action__in=("sap.customer_code_created", "sap.customer_code_reused"),
        )
        audit.new_value_json = {**audit.new_value_json, "review_drift": True}
        audit.save(update_fields=["new_value_json"])

        response = self.client.get("/api/v1/loan-accounts/", **self.auth)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])


class AssignedSapUntestedDriftProbe(SapStaffWorkspaceApiTests):
    def test_send_body_drift_affects_neither_total_nor_page(self):
        request_id = self.fixture._create_and_send("review-s37-body-drift")
        audit = AuditLog.objects.get(
            entity_type="sap_customer_profile_request",
            entity_id=request_id,
            action="finance.sap_customer_code.sent",
        )
        audit.new_value_json = {**audit.new_value_json, "review_drift": True}
        audit.save(update_fields=["new_value_json"])

        response = self.client.get(
            "/api/v1/disbursement-workspaces/",
            **self.fixture._auth(self.fixture.assignee),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])


class CfcUntestedDriftProbe(DisbursementWorkspaceApiTests):
    def test_initiation_body_drift_affects_neither_total_nor_page(self):
        audit = self.row.initiation_audit
        audit.new_value_json = {
            **audit.new_value_json,
            "maker_team_codes": ["drifted-after-initiation"],
        }
        audit.save(update_fields=["new_value_json"])

        response = self.client.get(
            "/api/v1/disbursement-workspaces/",
            **self.fixture.fixture._auth(self.fixture.cfc),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])
