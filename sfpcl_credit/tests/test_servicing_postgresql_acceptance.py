import json
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless

from django.db import close_old_connections, connection
from django.test import Client, TransactionTestCase

from sfpcl_credit.tests.test_direct_repayment_posting_api import (
    DirectRepaymentPostingApiTests,
)
from sfpcl_credit.tests.test_repayment_allocation_api import RepaymentAllocationApiTests


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class DirectRepaymentPostingPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = DirectRepaymentPostingApiTests(
            "test_valid_direct_receipt_and_exact_replay_create_one_pending_obligation"
        )
        fixture.setUp()
        self.fixture = fixture
        self.url = f"/api/v1/loan-accounts/{fixture.account.pk}/repayments/"

    def test_concurrent_same_idempotency_key_retains_one_receipt_and_obligation(self):
        payload = self.fixture._payload()
        statuses = self._race(
            (payload, "postgres-key-same"),
            (payload, "postgres-key-same"),
        )
        self.assertEqual(statuses, [200, 200])
        self._assert_single_chain()

    def test_concurrent_canonical_bank_reference_retains_one_receipt_and_obligation(self):
        payload = self.fixture._payload()
        changed_case = {
            **payload,
            "bank_reference_number": payload["bank_reference_number"].lower(),
        }
        statuses = self._race(
            (payload, "postgres-reference-a"),
            (changed_case, "postgres-reference-b"),
        )
        self.assertEqual(statuses, [200, 409])
        self._assert_single_chain()

    def _race(self, *requests):
        barrier = Barrier(len(requests))

        def submit(item):
            close_old_connections()
            barrier.wait()
            response = Client().post(
                self.url,
                data=json.dumps(item[0]),
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY=item[1],
                **self.fixture.auth,
            )
            close_old_connections()
            return response.status_code

        with ThreadPoolExecutor(max_workers=len(requests)) as pool:
            return sorted(pool.map(submit, requests))

    def _assert_single_chain(self):
        from sfpcl_credit.communications.models import Notification
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import Repayment, RepaymentSapPostingObligation

        self.assertEqual(Repayment.objects.count(), 1)
        self.assertEqual(RepaymentSapPostingObligation.objects.count(), 1)
        self.assertEqual(
            Notification.objects.filter(
                notification_type="repayment_sap_posting_due"
            ).count(),
            1,
        )
        self.assertEqual(
            AuditLog.objects.filter(action="repayment.receipt_created").count(), 1
        )


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class PrincipalFirstAllocationPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = RepaymentAllocationApiTests(
            "test_partial_receipt_reduces_principal_and_appends_immutable_evidence"
        )
        fixture.setUp()
        self.fixture = fixture
        captured = fixture.fixture._capture(
            fixture.fixture._payload(), "postgres-allocation-receipt"
        )
        self.repayment_id = captured.json()["data"]["repayment_id"]
        self.url = f"/api/v1/repayments/{self.repayment_id}/allocate/"

    def test_five_concurrent_allocations_retain_one_balance_transition_and_ledger_row(self):
        barrier = Barrier(5)

        def submit(_):
            close_old_connections()
            barrier.wait()
            response = Client().post(
                self.url,
                data=json.dumps(
                    {
                        "allocation_rule": "principal_first",
                        "remarks": "Concurrent allocation under the approved SOP.",
                    }
                ),
                content_type="application/json",
                **self.fixture.auth,
            )
            close_old_connections()
            return response.status_code

        with ThreadPoolExecutor(max_workers=5) as pool:
            statuses = sorted(pool.map(submit, range(5)))

        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import (
            LoanAccount,
            RepaymentAllocation,
            RepaymentLedgerEntry,
        )

        self.assertEqual(statuses, [200, 200, 200, 200, 200])
        account = LoanAccount.objects.get(pk=self.fixture.account.pk)
        self.assertEqual(str(account.principal_outstanding), "300000.00")
        self.assertEqual(str(account.total_outstanding), "300000.00")
        self.assertEqual(RepaymentAllocation.objects.count(), 1)
        self.assertEqual(RepaymentLedgerEntry.objects.count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="repayment.allocated").count(), 1)
