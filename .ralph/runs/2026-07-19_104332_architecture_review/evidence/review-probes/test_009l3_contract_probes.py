"""Review-only probes for the 009L3 public-owner contracts.

These intentionally assert the binding slice behavior and are not production tests.
They remain with the architecture-review evidence when current code violates it.
"""

from copy import copy
from datetime import timedelta
from uuid import uuid4

from django.test import TestCase
from django.utils import timezone

from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest
from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
    get_account_customer_code,
    get_customer_code_for_member,
)


class Epic009L3ContractReviewProbes(TestCase):
    def test_member_and_account_facades_reject_newer_cross_application_drift_identically(self):
        from sfpcl_credit.applications.models import LoanApplication
        from sfpcl_credit.loans.models import LoanAccount
        from sfpcl_credit.tests.test_disbursement_transfer_success_api import (
            DisbursementTransferSuccessApiTests,
        )

        fixture = DisbursementTransferSuccessApiTests(
            "test_public_success_records_transfer_and_activates_exact_loan_atomically"
        )
        fixture.setUp()
        transferred = fixture._post(
            bank_reference_number="RBL-REVIEW-DUPLICATE-001",
            disbursed_at=timezone.now(),
        )
        self.assertEqual(transferred.status_code, 200, transferred.content)
        account = LoanAccount.objects.get(
            pk=fixture.owner.fixture.application.loan_account.pk
        )
        original = SapCustomerProfileRequest.objects.get(
            loan_application_id=account.loan_application_id,
            request_status=SapCustomerProfileRequest.STATUS_COMPLETED,
        )
        later_application = copy(original.loan_application)
        later_application._state = copy(original.loan_application._state)
        later_application._state.adding = True
        later_application.pk = uuid4()
        later_application.application_reference_number = "LO-REVIEW-CROSS-APP"
        later_application.created_at = original.loan_application.created_at + timedelta(days=1)
        later_application.save(force_insert=True)
        stale_cross_application = copy(original)
        stale_cross_application._state = copy(original._state)
        stale_cross_application._state.adding = True
        stale_cross_application.pk = uuid4()
        stale_cross_application.loan_application = later_application
        stale_cross_application.created_at = original.created_at + timedelta(days=1)
        stale_cross_application.save(force_insert=True)

        member_decision = get_customer_code_for_member(account.member_id)
        account_decision = get_account_customer_code(
            application_id=account.loan_application_id,
            member_id=account.member_id,
            customer_code_id=account.sap_customer_code_id,
        )

        self.assertIsNone(member_decision)
        self.assertIsNone(account_decision)
