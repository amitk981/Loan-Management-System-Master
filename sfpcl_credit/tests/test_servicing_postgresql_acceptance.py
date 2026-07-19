import json
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless

from django.db import close_old_connections, connection
from django.test import Client, TransactionTestCase

from sfpcl_credit.tests.test_direct_repayment_posting_api import (
    DirectRepaymentPostingApiTests,
)


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
