"""Review-only probes for 2026-07-17_164724_architecture_review.

These intentionally describe source/slice-required behaviour and are expected to fail against
the reviewed product commit. They live only in the run evidence directory.
"""

from django.test import TestCase
from django.utils import timezone

from sfpcl_credit.communications.models import Communication
from sfpcl_credit.tests.test_disbursement_advice_api import (
    DisbursementAdviceApiTests,
)
from sfpcl_credit.tests.test_disbursement_transfer_success_api import (
    DisbursementTransferSuccessApiTests,
)


class TransferReplayContractProbe(TestCase):
    def test_exact_replay_uses_api_45_2_shape(self):
        fixture = DisbursementTransferSuccessApiTests(
            "test_public_success_records_transfer_and_activates_exact_loan_atomically"
        )
        fixture.setUp()
        accepted_at = timezone.now()

        first = fixture._post(
            bank_reference_number="REVIEW-REPLAY-0001",
            disbursed_at=accepted_at,
        )
        replay = fixture._post(
            bank_reference_number="REVIEW-REPLAY-0001",
            disbursed_at=accepted_at,
        )

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertTrue(replay.json()["data"]["idempotency_replayed"])
        self.assertEqual(
            replay.json()["data"]["original_response"], first.json()["data"]
        )


class AdviceCurrentTruthProbes(TestCase):
    def setUp(self):
        self.fixture = DisbursementAdviceApiTests(
            "test_public_success_sends_exact_advice_without_financial_side_effects"
        )
        self.fixture.setUp()

    def test_changed_rendered_snapshot_makes_replay_conflict(self):
        first = self.fixture._post()
        self.assertEqual(first.status_code, 200, first.content)
        Communication.objects.filter(
            pk=first.json()["data"]["disbursement_advice_communication_id"]
        ).update(body_snapshot="changed after delivery")

        replay = self.fixture._post()

        self.assertEqual(replay.status_code, 409, replay.content)

    def test_changed_canonical_email_makes_old_recipient_replay_conflict(self):
        first = self.fixture._post()
        self.assertEqual(first.status_code, 200, first.content)
        member = self.fixture.row.member
        member.email = "new.borrower.address@example.com"
        member.save(update_fields=["email"])

        replay = self.fixture._post(email="borrower.advice@example.com")

        self.assertEqual(replay.status_code, 409, replay.content)

    def test_cfc_cannot_send_advice_under_source_role_matrix(self):
        self.assertIn(
            "chief_financial_controller",
            self.fixture.actor.role_codes(),
        )

        response = self.fixture._post()

        self.assertEqual(response.status_code, 403, response.content)
