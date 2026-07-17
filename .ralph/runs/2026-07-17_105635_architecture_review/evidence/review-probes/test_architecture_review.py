"""Review-only probes for the 2026-07-17 architecture review.

These tests describe source/slice-required behavior that the retained implementation
does not yet satisfy. They are evidence only and are not part of the production suite.
"""

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone


class ArchitectureReviewProbeTests(TestCase):
    def _initiation_fixture(self):
        from sfpcl_credit.tests.test_disbursement_initiation_api import (
            DisbursementInitiationApiTests,
        )

        fixture = DisbursementInitiationApiTests(
            "test_current_ready_payment_is_recorded_once_without_transfer_side_effects"
        )
        fixture.setUp()
        return fixture

    def _authorisation_fixture(self):
        from sfpcl_credit.tests.test_disbursement_authorisation_api import (
            DisbursementAuthorisationApiTests,
        )

        fixture = DisbursementAuthorisationApiTests(
            "test_cfc_approval_is_terminal_evidence_but_not_bank_execution"
        )
        fixture.setUp()
        return fixture

    def test_positive_lesser_amount_within_sanction_can_be_initiated(self):
        fixture = self._initiation_fixture()

        response = fixture._post(
            changes={"disbursement_amount": "399999.99"},
            key="architecture-review-lesser-amount",
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["data"]["initiation_status"], "initiated")

    def test_active_source_bank_governance_requires_atomic_evidence(self):
        from sfpcl_credit.configurations.models import SourceBankAccountGovernance

        fixture = self._initiation_fixture()

        with self.assertRaises(IntegrityError):
            SourceBankAccountGovernance.objects.create(
                bank_account_id=fixture.source_bank_id,
                source_facts_digest="a" * 64,
                reason_digest="b" * 64,
                request_id="architecture-review-unproved-source-bank",
                activated_by_user=fixture.actor,
                activated_at=timezone.now(),
                version_history=None,
                activation_audit=None,
            )

    def test_changed_borrower_bank_fact_blocks_cfc_authorisation(self):
        from sfpcl_credit.disbursements.models import Disbursement
        from sfpcl_credit.members.models import BankAccount

        fixture = self._authorisation_fixture()
        row = Disbursement.objects.get(pk=fixture.disbursement_id)
        BankAccount.objects.filter(pk=row.borrower_bank_account_id).update(
            ifsc="CHANGED00001"
        )

        response = fixture._post(
            "approved", "Beneficiary and instruction verified."
        )

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(response.json()["error"]["code"], "CONFLICT")

    def test_preexisting_transfer_truth_blocks_cfc_authorisation(self):
        from sfpcl_credit.disbursements.models import Disbursement

        fixture = self._authorisation_fixture()
        Disbursement.objects.filter(pk=fixture.disbursement_id).update(
            bank_reference_number="PREEXISTING-UTR",
            disbursed_at=timezone.now(),
            loan_register_updated_flag=True,
        )

        response = fixture._post(
            "approved", "Beneficiary and instruction verified."
        )

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(response.json()["error"]["code"], "CONFLICT")
