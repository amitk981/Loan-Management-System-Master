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
from sfpcl_credit.tests.test_bank_statement_matching_api import (
    BankStatementMatchingApiTests,
)
from sfpcl_credit.tests.test_subsidiary_deduction_reconciliation_api import (
    SubsidiaryDeductionReconciliationApiTests,
)
from sfpcl_credit.tests.test_interest_invoice_api import InterestInvoiceApiTests
from sfpcl_credit.tests.test_interest_accrual_api import MonthlyInterestAccrualApiTests
from sfpcl_credit.tests.test_interest_capitalisation_api import (
    InterestCapitalisationApiTests,
)
from sfpcl_credit.tests.test_dpd_monitoring_api import DpdMonitoringApiTests


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class DpdSnapshotPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        from datetime import date

        from sfpcl_credit.loans.models import RepaymentSchedule

        fixture = DpdMonitoringApiTests(
            "test_calculate_first_overdue_day_from_schedule_truth"
        )
        fixture.setUp()
        RepaymentSchedule.objects.create(
            loan_account=fixture.account,
            installment_number=1,
            due_date=date(2026, 6, 30),
            principal_due="1000.00",
            interest_due="100.00",
            charges_due="0.00",
            total_due="1100.00",
            schedule_status="pending",
        )
        self.fixture = fixture

    def test_same_date_race_retains_one_snapshot_audit_and_current_pointer(self):
        barrier = Barrier(2)

        def submit(_):
            close_old_connections()
            try:
                barrier.wait(timeout=15)
                return Client().post(
                    f"/api/v1/loan-accounts/{self.fixture.account.pk}/dpd-status/calculate/",
                    data=json.dumps({"as_of_date": "2026-07-01"}),
                    content_type="application/json",
                    **self.fixture.auth,
                ).status_code
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = sorted(pool.map(submit, range(2)))

        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.monitoring.models import DpdStatus

        self.fixture.account.refresh_from_db()
        row = DpdStatus.objects.get()
        self.assertEqual(statuses, [200, 200])
        self.assertEqual(
            AuditLog.objects.filter(action="monitoring.dpd.calculated").count(), 1
        )
        self.assertEqual(self.fixture.account.current_dpd_status_id, row.pk)


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class InterestCapitalisationPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = InterestCapitalisationApiTests(
            "test_may_first_finalisation_moves_principal_once_and_retains_intimation_chain"
        )
        fixture.setUp()
        self.fixture = fixture

    def test_concurrent_finalisation_retains_one_principal_and_ledger_movement(self):
        barrier = Barrier(2)

        def submit(index):
            close_old_connections()
            barrier.wait()
            response = Client().post(
                f"/api/v1/loan-accounts/{self.fixture.account.pk}/interest-capitalisations/",
                data=json.dumps(
                    {
                        "financial_year": "FY2026-27",
                        "capitalisation_date": "2027-05-01",
                    }
                ),
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY=f"postgres-interest-capitalisation-{index}",
                **self.fixture.auth,
            )
            close_old_connections()
            return response.status_code

        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = sorted(pool.map(submit, range(2)))

        from sfpcl_credit.interest.models import (
            InterestCapitalisation,
            InterestCapitalisationLedgerEntry,
        )

        self.fixture.account.refresh_from_db()
        self.assertEqual(statuses, [200, 409])
        self.assertEqual(InterestCapitalisation.objects.count(), 1)
        self.assertEqual(InterestCapitalisationLedgerEntry.objects.count(), 1)
        self.assertEqual(str(self.fixture.account.principal_outstanding), "437000.00")


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class MonthlyInterestAccrualPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = MonthlyInterestAccrualApiTests(
            "test_single_month_uses_server_owned_snapshots_and_creates_pending_sap_obligation"
        )
        fixture.setUp()
        self.fixture = fixture

    def test_concurrent_same_month_retains_one_accrual_and_sap_obligation(self):
        barrier = Barrier(2)

        def submit(index):
            close_old_connections()
            barrier.wait()
            response = Client().post(
                f"/api/v1/loan-accounts/{self.fixture.account.pk}/accrual-entries/",
                data=json.dumps({"accrual_month": "2026-07"}),
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY=f"postgres-interest-accrual-{index}",
                **self.fixture.auth,
            )
            close_old_connections()
            return response.status_code

        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = sorted(pool.map(submit, range(2)))

        from sfpcl_credit.configurations.models import InterestRateConsumptionSnapshot
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.interest.models import AccrualEntry, AccrualSapPostingObligation

        self.assertEqual(statuses, [200, 409])
        self.assertEqual(AccrualEntry.objects.count(), 1)
        self.assertEqual(AccrualSapPostingObligation.objects.count(), 1)
        self.assertEqual(InterestRateConsumptionSnapshot.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="interest.accrual.generated").count(), 1
        )


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class InterestInvoicePostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = InterestInvoiceApiTests(
            "test_generation_uses_server_owned_fy_truth_and_leaves_balances_unchanged"
        )
        fixture.setUp()
        self.fixture = fixture

    def test_concurrent_same_period_retains_one_immutable_invoice(self):
        barrier = Barrier(2)

        def submit(index):
            close_old_connections()
            barrier.wait()
            response = Client().post(
                f"/api/v1/loan-accounts/{self.fixture.account.pk}/interest-invoices/",
                data=json.dumps({"financial_year": "FY2026-27"}),
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY=f"postgres-interest-invoice-{index}",
                **self.fixture.auth,
            )
            close_old_connections()
            return response.status_code

        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = sorted(pool.map(submit, range(2)))

        from sfpcl_credit.configurations.models import InterestRateConsumptionSnapshot
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.interest.models import InterestInvoice

        self.assertEqual(statuses, [200, 409])
        self.assertEqual(InterestInvoice.objects.count(), 1)
        self.assertEqual(InterestRateConsumptionSnapshot.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="interest.invoice.generated").count(), 1
        )


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class InterestAccountingOwnerPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def test_exact_invoice_key_race_replays_one_frozen_generation(self):
        fixture = self._invoice_fixture()
        statuses = self._race(
            lambda _: Client().post(
                f"/api/v1/loan-accounts/{fixture.account.pk}/interest-invoices/",
                data=json.dumps({"financial_year": "FY2026-27"}),
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="owner-invoice-exact",
                **fixture.auth,
            )
        )
        from sfpcl_credit.interest.models import InterestInvoice

        self.assertEqual(statuses, [200, 200])
        row = InterestInvoice.objects.get()
        self.assertTrue(row.generation_original_response_json)

    def test_changed_invoice_key_race_is_one_effect_and_one_conflict(self):
        fixture = self._invoice_fixture()
        statuses = self._race(
            lambda index: Client().post(
                f"/api/v1/loan-accounts/{fixture.account.pk}/interest-invoices/",
                data=json.dumps({"financial_year": "FY2026-27"}),
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY=f"owner-invoice-changed-{index}",
                **fixture.auth,
            )
        )
        from sfpcl_credit.interest.models import InterestInvoice

        self.assertEqual(statuses, [200, 409])
        self.assertEqual(InterestInvoice.objects.count(), 1)

    def test_exact_accrual_key_race_replays_one_month_and_obligation(self):
        fixture = MonthlyInterestAccrualApiTests(
            "test_single_month_uses_server_owned_snapshots_and_creates_pending_sap_obligation"
        )
        fixture.setUp()
        statuses = self._race(
            lambda _: Client().post(
                f"/api/v1/loan-accounts/{fixture.account.pk}/accrual-entries/",
                data=json.dumps({"accrual_month": "2026-07"}),
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="owner-accrual-exact",
                **fixture.auth,
            )
        )
        from sfpcl_credit.interest.models import AccrualEntry, AccrualSapPostingObligation

        self.assertEqual(statuses, [200, 200])
        self.assertEqual(AccrualEntry.objects.count(), 1)
        self.assertEqual(AccrualSapPostingObligation.objects.count(), 1)

    def test_changed_capitalisation_key_race_moves_money_once(self):
        fixture = InterestCapitalisationApiTests(
            "test_may_first_finalisation_moves_principal_once_and_retains_intimation_chain"
        )
        fixture.setUp()
        statuses = self._race(
            lambda index: Client().post(
                f"/api/v1/loan-accounts/{fixture.account.pk}/interest-capitalisations/",
                data=json.dumps(
                    {
                        "financial_year": "FY2026-27",
                        "capitalisation_date": "2027-05-01",
                    }
                ),
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY=f"owner-capitalisation-changed-{index}",
                **fixture.auth,
            )
        )
        from sfpcl_credit.interest.models import (
            InterestCapitalisation,
            InterestCapitalisationLedgerEntry,
        )

        self.assertEqual(statuses, [200, 409])
        self.assertEqual(InterestCapitalisation.objects.count(), 1)
        self.assertEqual(InterestCapitalisationLedgerEntry.objects.count(), 1)

    def test_partial_delivery_replay_and_reverse_consumers_keep_original_truth(self):
        fixture = InterestCapitalisationApiTests(
            "test_may_first_finalisation_moves_principal_once_and_retains_intimation_chain"
        )
        fixture.setUp()
        first = fixture._capitalise("owner-capitalisation-exact")
        from sfpcl_credit.communications.models import CommunicationDeliveryJob
        from sfpcl_credit.interest.models import (
            InterestCapitalisation,
            InterestCapitalisationHardCopyTask,
        )

        row = InterestCapitalisation.objects.get()
        job = CommunicationDeliveryJob.objects.get(
            communication_id=row.borrower_intimation_email_id
        )
        job.status = CommunicationDeliveryJob.STATUS_FAILED
        job.attempts = job.max_attempts
        job.last_failure_code = "provider_rejected"
        job.save(update_fields=["status", "attempts", "last_failure_code"])
        replay = fixture._capitalise("owner-capitalisation-exact")
        ledger = Client().get(
            f"/api/v1/loan-accounts/{fixture.account.pk}/ledger/", **fixture.auth
        )

        self.assertEqual(replay.json()["data"]["original_response"], first.json()["data"])
        self.assertEqual(ledger.status_code, 200, ledger.content)
        self.assertEqual(ledger.json()["data"][-1]["transaction_type"], "interest_capitalisation")
        self.assertEqual(InterestCapitalisationHardCopyTask.objects.count(), 1)

    @staticmethod
    def _invoice_fixture():
        fixture = InterestInvoiceApiTests(
            "test_generation_uses_server_owned_fy_truth_and_leaves_balances_unchanged"
        )
        fixture.setUp()
        return fixture

    @staticmethod
    def _race(submit):
        barrier = Barrier(2)

        def worker(index):
            close_old_connections()
            barrier.wait()
            response = submit(index)
            close_old_connections()
            return response.status_code

        with ThreadPoolExecutor(max_workers=2) as pool:
            return sorted(pool.map(worker, range(2)))


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
class SubsidiaryDeductionPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = SubsidiaryDeductionReconciliationApiTests(
            "test_verified_agreement_allows_subsidiary_deduction_capture"
        )
        fixture.setUp()
        fixture._verified_tri_party_agreement()
        self.fixture = fixture
        self.capture_url = f"/api/v1/loan-accounts/{fixture.account.pk}/repayments/"

    def test_concurrent_same_deduction_retains_one_receipt_evidence_and_task(self):
        payload = self.fixture._payload()
        barrier = Barrier(2)

        def submit(_):
            close_old_connections()
            barrier.wait()
            response = Client().post(
                self.capture_url,
                data=json.dumps(payload),
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="postgres-subsidiary-capture",
                **self.fixture.auth,
            )
            close_old_connections()
            return response.status_code

        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = sorted(pool.map(submit, range(2)))

        from sfpcl_credit.communications.models import Notification
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import (
            Repayment,
            RepaymentSapPostingObligation,
            SubsidiaryDeductionEvidence,
        )

        self.assertEqual(statuses, [200, 200])
        self.assertEqual(Repayment.objects.count(), 1)
        self.assertEqual(SubsidiaryDeductionEvidence.objects.count(), 1)
        self.assertEqual(RepaymentSapPostingObligation.objects.count(), 1)
        self.assertEqual(
            Notification.objects.filter(
                notification_type="subsidiary_repayment_treasury_verification"
            ).count(),
            1,
        )
        self.assertEqual(
            AuditLog.objects.filter(action="repayment.receipt_created").count(), 1
        )

    def test_concurrent_verification_and_allocation_retain_one_match_and_movement(self):
        from sfpcl_credit.loans.models import (
            RepaymentAllocation,
            RepaymentLedgerEntry,
            RepaymentSchedule,
        )

        captured = self.fixture._capture(
            self.fixture._payload(), "postgres-subsidiary-e2e"
        )
        repayment_id = captured.json()["data"]["repayment_id"]
        imported = self.fixture.fixture._upload(
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-15,2026-12-15,75000.00,Payment for "
            f"{self.fixture.account.member.legal_name} application "
            f"{self.fixture.account.loan_application.application_reference_number},"
            f"SUB-TRANSFER-001,{self.fixture.account.loan_account_number}\n",
            key="postgres-subsidiary-statement",
        )
        self.assertEqual(imported.status_code, 200, imported.content)
        RepaymentSchedule.objects.create(
            loan_account=self.fixture.account,
            installment_number=1,
            due_date=self.fixture.account.repayment_date,
            principal_due=self.fixture.account.principal_outstanding,
            interest_due=self.fixture.account.interest_outstanding,
            charges_due=self.fixture.account.charges_outstanding,
            total_due=self.fixture.account.total_outstanding,
            schedule_status="pending",
        )
        verify_url = (
            f"/api/v1/repayments/{repayment_id}/verify-subsidiary-deduction/"
        )
        verify_statuses = self._race_post(
            verify_url,
            {"remarks": "Concurrent Treasury evidence verification."},
            key=None,
        )
        self.assertEqual(verify_statuses, [200, 200])
        posted = self.fixture._mark_sap(repayment_id)
        self.assertEqual(posted.status_code, 200, posted.content)
        allocation_statuses = self._race_post(
            f"/api/v1/repayments/{repayment_id}/allocate/",
            {
                "allocation_rule": "principal_first",
                "remarks": "Concurrent canonical subsidiary allocation.",
            },
            key="postgres-subsidiary-allocation",
        )

        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import BankStatementLine

        self.assertEqual(allocation_statuses, [200, 200])
        self.assertEqual(
            BankStatementLine.objects.filter(
                matched_repayment_id=repayment_id, match_status="matched"
            ).count(),
            1,
        )
        self.assertEqual(RepaymentAllocation.objects.count(), 1)
        self.assertEqual(RepaymentLedgerEntry.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(
                action="repayment.subsidiary_treasury_verified"
            ).count(),
            1,
        )

    def _race_post(self, url, payload, *, key):
        barrier = Barrier(2)

        def submit(_):
            close_old_connections()
            barrier.wait()
            headers = dict(self.fixture.auth)
            if key is not None:
                headers["HTTP_IDEMPOTENCY_KEY"] = key
            response = Client().post(
                url,
                data=json.dumps(payload),
                content_type="application/json",
                **headers,
            )
            close_old_connections()
            return response.status_code

        with ThreadPoolExecutor(max_workers=2) as pool:
            return sorted(pool.map(submit, range(2)))


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


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class BankStatementMatchingPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = BankStatementMatchingApiTests(
            "test_manual_match_requires_reason_and_one_receipt_cannot_be_consumed_twice"
        )
        fixture.setUp()
        self.fixture = fixture
        captured = fixture.fixture._capture(
            {
                **fixture.fixture._payload(),
                "amount_received": "60000.00",
                "received_date": "2026-12-09",
                "bank_reference_number": "UTR-PG-STATEMENT-MATCH",
            },
            "postgres-statement-receipt",
        )
        self.repayment_id = captured.json()["data"]["repayment_id"]
        imported = fixture._upload(
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-09,2026-12-09,60000.00,Race candidate A,UNKNOWN-PG-A,"
            f"{fixture.account.loan_account_number}\n"
            f"2026-12-09,2026-12-09,60000.00,Race candidate B,UNKNOWN-PG-B,"
            f"{fixture.account.loan_account_number}\n",
            key="postgres-statement-import",
        ).json()["data"]
        self.line_ids = [line["bank_statement_line_id"] for line in imported["lines"]]

    def test_concurrent_manual_matches_retain_one_statement_counterpart(self):
        barrier = Barrier(2)

        def submit(line_id):
            close_old_connections()
            barrier.wait()
            response = Client().post(
                f"/api/v1/bank-statement-lines/{line_id}/match/",
                data=json.dumps(
                    {
                        "repayment_id": self.repayment_id,
                        "reason": "Authorised concurrent reconciliation review.",
                    }
                ),
                content_type="application/json",
                **self.fixture.auth,
            )
            close_old_connections()
            return response.status_code

        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = sorted(pool.map(submit, self.line_ids))

        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import BankStatementLine, Repayment

        self.assertEqual(statuses, [200, 409])
        repayment = Repayment.objects.get(pk=self.repayment_id)
        self.assertEqual(repayment.statement_match_status, "manual_match_exception")
        self.assertEqual(
            BankStatementLine.objects.filter(
                matched_repayment_id=self.repayment_id, match_status="matched"
            ).count(),
            1,
        )
        self.assertEqual(
            str(repayment.bank_statement_line_id),
            str(
                BankStatementLine.objects.get(
                    matched_repayment_id=self.repayment_id
                ).pk
            ),
        )
        self.assertEqual(
            AuditLog.objects.filter(
                action="bank_statement.line_manually_matched"
            ).count(),
            1,
        )
