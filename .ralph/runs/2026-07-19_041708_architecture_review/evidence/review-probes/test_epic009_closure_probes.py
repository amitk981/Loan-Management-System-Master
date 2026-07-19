"""Review-only probes for Epic 009 closure; never imported by production tests."""

from django.test import Client, TestCase

from sfpcl_credit.disbursements.models import Disbursement
from sfpcl_credit.disbursements.modules.current_disbursement_evidence import (
    resolve_current_disbursement_evidence,
)


class StaleDisbursementWorkspaceProjectionProbe(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_disbursement_authorisation_api import (
            DisbursementAuthorisationApiTests,
        )

        fixture = DisbursementAuthorisationApiTests(
            "test_cfc_approval_is_terminal_evidence_but_not_bank_execution"
        )
        fixture.setUp()
        approved = fixture._post(
            "approved", "Independent transfer authorisation retained."
        )
        self.assertEqual(approved.status_code, 200, approved.content)
        self.fixture = fixture
        self.row = Disbursement.objects.get(pk=fixture.disbursement_id)
        self.client = Client()

    def test_admitted_finance_actor_does_not_hit_uncaught_internal_permission(self):
        self.client.raise_request_exception = False

        response = self.client.get(
            "/api/v1/disbursement-workspaces/",
            **self.fixture.fixture._auth(self.fixture.fixture.actor),
        )

        self.assertEqual(response.status_code, 200, response.content)

    def test_incoherent_approved_row_does_not_advertise_transfer_action(self):
        self.fixture.fixture.fixture._grant(
            self.fixture.fixture.actor, "finance.loan_account.read"
        )
        Disbursement.objects.filter(pk=self.row.pk).update(
            final_verification_comments="Changed after the immutable initiation ledger."
        )
        self.row.refresh_from_db()
        self.assertIsNone(
            resolve_current_disbursement_evidence(
                disbursement_id=self.row.pk,
                allowed_authorisation_statuses=("approved",),
            )
        )

        response = self.client.get(
            "/api/v1/disbursement-workspaces/",
            **self.fixture.fixture._auth(self.fixture.fixture.actor),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["data"], [])
