"""Self-contained copies of the five 009L4 probes that 009L5 must close."""

from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from django.test import SimpleTestCase

from sfpcl_credit.disbursements.models import Disbursement
from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.processes.portal_disbursement_status import (
    _current_pre_payment_stages,
)
from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest
from sfpcl_credit.tests.test_disbursement_workspace_api import (
    DisbursementWorkspaceApiTests,
    SapStaffWorkspaceApiTests,
)
from sfpcl_credit.tests.test_loan_account_reads_api import (
    ActiveLoanAccountReadApiTests,
    LoanAccountReadApiTests,
)


class LoanAccountRetainedProbe(LoanAccountReadApiTests):
    def test_nonqueryable_creation_drift_affects_neither_total_nor_page(self):
        audit = AuditLog.objects.get(
            action="finance.loan_account.created",
            entity_id=self.account.pk,
        )
        audit.new_value_json = {**audit.new_value_json, "actor_role_codes": []}
        audit.save(update_fields=["new_value_json"])

        response = self.client.get("/api/v1/loan-accounts/", **self.auth)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])


class SapCompletionRetainedProbe(ActiveLoanAccountReadApiTests):
    def test_completion_digest_drift_affects_neither_total_nor_page(self):
        request = SapCustomerProfileRequest.objects.get(
            loan_application_id=self.account.loan_application_id,
            request_status=SapCustomerProfileRequest.STATUS_COMPLETED,
        )
        audit = AuditLog.objects.get(
            entity_type="sap_customer_profile_request",
            entity_id=request.pk,
            action__in=("sap.customer_code_created", "sap.customer_code_reused"),
        )
        audit.new_value_json = {
            **audit.new_value_json,
            "completion_input_digest": "0" * 64,
        }
        audit.save(update_fields=["new_value_json"])

        response = self.client.get("/api/v1/loan-accounts/", **self.auth)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])


class AssignedSapRetainedProbe(SapStaffWorkspaceApiTests):
    def test_send_digest_drift_affects_neither_total_nor_page(self):
        request_id = self.fixture._create_and_send("review-s37-selector-drift")
        audit = AuditLog.objects.get(
            entity_type="sap_customer_profile_request",
            entity_id=request_id,
            action="finance.sap_customer_code.sent",
        )
        audit.new_value_json = {
            **audit.new_value_json,
            "annexure_checksum_sha256": "0" * 64,
        }
        audit.save(update_fields=["new_value_json"])

        response = self.client.get(
            "/api/v1/disbursement-workspaces/",
            **self.fixture._auth(self.fixture.assignee),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])


class CfcRetainedProbe(DisbursementWorkspaceApiTests):
    def test_stale_initiation_affects_neither_total_nor_page(self):
        Disbursement.objects.filter(pk=self.row.pk).update(
            final_verification_comments="Changed after immutable initiation evidence."
        )

        response = self.client.get(
            "/api/v1/disbursement-workspaces/",
            **self.fixture.fixture._auth(self.fixture.cfc),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])


class PortalRetainedProbe(SimpleTestCase):
    @patch(
        "sfpcl_credit.processes.portal_disbursement_status.resolve_legal_readiness",
        return_value=SimpleNamespace(
            documentation_complete=True,
            documentation_completed_at=None,
        ),
    )
    @patch(
        "sfpcl_credit.processes.portal_disbursement_status.get_customer_code_for_member"
    )
    def test_other_application_completion_does_not_complete_requested_application_stage(
        self, member_code, _legal
    ):
        application_id = uuid4()
        member_id = uuid4()
        member_code.return_value = SimpleNamespace(
            customer_code_id=uuid4(),
            member_id=member_id,
            loan_application_id=uuid4(),
            status="active",
            completed_at=None,
        )

        stages = _current_pre_payment_stages(
            application_id=application_id,
            member_id=member_id,
        )

        self.assertFalse(stages["completed"]["sap_setup"])
