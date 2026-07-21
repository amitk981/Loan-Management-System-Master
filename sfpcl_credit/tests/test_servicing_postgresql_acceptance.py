import json
import tempfile
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless

from django.db import close_old_connections, connection
from django.test import Client, TransactionTestCase, override_settings

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
from sfpcl_credit.tests.test_reminder_queue_api import ReminderQueueApiTests
from sfpcl_credit.tests.test_quarterly_mis_api import QuarterlyMisApiTests


@override_settings(
    DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-interest-policy-pg-tests-")
)
@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class InterestPolicyIntegrityPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def test_approved_policy_rejects_orm_bulk_and_database_mutation_paths(self):
        from datetime import date

        from django.core.exceptions import ValidationError
        from django.db import IntegrityError, transaction

        from sfpcl_credit.interest.models import InterestInvoiceConfiguration
        from sfpcl_credit.tests.servicing_builders import (
            build_approved_interest_calculation_policy,
            build_servicing_owner_fixture,
        )

        fixture = build_servicing_owner_fixture(suffix="policy-pg")
        policy = build_approved_interest_calculation_policy(
            fixture=fixture,
            version="POLICY-PG-IMMUTABLE",
        )
        policy.day_count_basis = 360
        with self.assertRaises(ValidationError):
            policy.save(update_fields=["day_count_basis"])
        with self.assertRaises(ValidationError):
            InterestInvoiceConfiguration.objects.filter(pk=policy.pk).update(
                day_count_basis=360
            )
        with self.assertRaises(ValidationError):
            InterestInvoiceConfiguration.objects.bulk_update(
                [policy], ["day_count_basis"]
            )
        with self.assertRaises(ValidationError):
            policy.delete()
        with self.assertRaises(ValidationError):
            InterestInvoiceConfiguration.objects.filter(pk=policy.pk).delete()
        with self.assertRaises(IntegrityError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE interest_invoice_configurations "
                    "SET day_count_basis = %s "
                    "WHERE interest_invoice_configuration_id = %s",
                    [360, policy.pk],
                )
        with self.assertRaises(IntegrityError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM interest_invoice_configurations "
                    "WHERE interest_invoice_configuration_id = %s",
                    [policy.pk],
                )
        amendment = build_approved_interest_calculation_policy(
            fixture=fixture,
            version="POLICY-PG-AMENDMENT",
            effective_from=date(2027, 4, 1),
            effective_to=date(2028, 3, 31),
        )
        self.assertNotEqual(amendment.pk, policy.pk)

    def test_whole_decision_rounding_and_missing_policy_are_fail_closed(self):
        from datetime import date
        from decimal import Decimal

        from sfpcl_credit.interest.models import InterestInvoiceConfiguration
        from sfpcl_credit.interest.modules.as_of_accounting import decide_interest_as_of
        from sfpcl_credit.tests.servicing_builders import (
            activate_interest_rate,
            build_approved_interest_calculation_policy,
            build_interest_rate_proposal,
            build_servicing_owner_fixture,
        )

        fixture = build_servicing_owner_fixture(suffix="rounding-pg")
        type(fixture.account).objects.filter(pk=fixture.account.pk).update(
            disbursed_amount="1.00",
            principal_outstanding="1.00",
            total_outstanding="1.00",
        )
        fixture.account.refresh_from_db()
        for suffix, effective_from in (("A", date(2026, 4, 1)), ("B", date(2026, 4, 2))):
            proposal = build_interest_rate_proposal(
                fixture=fixture,
                version=f"POLICY-PG-RATE-{suffix}",
                effective_from=effective_from,
                rate="91.2500",
            )
            activate_interest_rate(
                fixture=fixture,
                proposal=proposal,
                idempotency_key=f"policy-pg-rate-{suffix.lower()}",
            )
        policy = build_approved_interest_calculation_policy(
            fixture=fixture,
            version="POLICY-PG-ROUNDING",
        )
        decision = decide_interest_as_of(
            account=fixture.account,
            period_start=date(2026, 4, 1),
            period_end=date(2026, 4, 2),
            configuration=policy,
        )
        self.assertEqual(decision.gross_interest_amount, Decimal("0.01"))
        missing = InterestInvoiceConfiguration.objects.create(
            version_number="POLICY-PG-MISSING",
            effective_from=date(2027, 4, 1),
            effective_to=date(2028, 3, 31),
            calculation_method="simple_daily",
            day_count_basis=365,
            tax_rate="0.0000",
            fixed_fee_amount="0.00",
            owner_role_codes=["accounts_head"],
            status="active",
            approved_by_user=fixture.maker,
        )
        with self.assertRaises(ValueError):
            decide_interest_as_of(
                account=fixture.account,
                period_start=date(2027, 4, 1),
                period_end=date(2027, 4, 2),
                configuration=missing,
            )

    def test_mismatched_reclassification_is_zero_write(self):
        from sfpcl_credit.interest.models import (
            InterestCapitalisation,
            InterestCapitalisationLedgerEntry,
        )
        from sfpcl_credit.tests.servicing_builders import (
            build_interest_capitalisation_fixture,
        )

        fixture = build_interest_capitalisation_fixture()
        fixture.account.interest_outstanding = "36999.99"
        fixture.account.total_outstanding = "436999.99"
        fixture.account.save(update_fields=["interest_outstanding", "total_outstanding"])
        response = fixture.submit(idempotency_key="policy-pg-mismatch")
        fixture.account.refresh_from_db()

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(str(fixture.account.principal_outstanding), "400000.00")
        self.assertEqual(InterestCapitalisation.objects.count(), 0)
        self.assertEqual(InterestCapitalisationLedgerEntry.objects.count(), 0)

    def test_exact_capitalisation_race_replays_one_byte_stable_decision(self):
        from sfpcl_credit.interest.models import (
            InterestCapitalisation,
            InterestCapitalisationLedgerEntry,
        )
        from sfpcl_credit.tests.servicing_builders import (
            build_interest_capitalisation_fixture,
        )

        fixture = build_interest_capitalisation_fixture()
        responses = self._race(
            lambda _: fixture.submit(idempotency_key="policy-pg-capitalisation-exact")
        )
        self.assertEqual(sorted(response.status_code for response in responses), [200, 200])
        original = next(
            response.json()["data"]
            for response in responses
            if not response.json()["data"].get("idempotency_replayed")
        )
        replay = next(
            response.json()["data"]
            for response in responses
            if response.json()["data"].get("idempotency_replayed")
        )
        self.assertEqual(replay["original_response"], original)
        fixture.account.refresh_from_db()
        self.assertEqual(str(fixture.account.principal_outstanding), "437000.00")
        self.assertEqual(InterestCapitalisation.objects.count(), 1)
        self.assertEqual(InterestCapitalisationLedgerEntry.objects.count(), 1)

    def test_changed_key_capitalisation_race_retains_one_reclassification(self):
        from sfpcl_credit.interest.models import (
            InterestCapitalisation,
            InterestCapitalisationLedgerEntry,
        )
        from sfpcl_credit.tests.servicing_builders import (
            build_interest_capitalisation_fixture,
        )

        fixture = build_interest_capitalisation_fixture()
        responses = self._race(
            lambda index: fixture.submit(
                idempotency_key=f"policy-pg-capitalisation-changed-{index}"
            )
        )
        self.assertEqual(sorted(response.status_code for response in responses), [200, 409])
        fixture.account.refresh_from_db()
        self.assertEqual(str(fixture.account.principal_outstanding), "437000.00")
        self.assertEqual(InterestCapitalisation.objects.count(), 1)
        self.assertEqual(InterestCapitalisationLedgerEntry.objects.count(), 1)

    @staticmethod
    def _race(submit):
        barrier = Barrier(2)

        def worker(index):
            close_old_connections()
            try:
                barrier.wait(timeout=15)
                return submit(index)
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            return list(pool.map(worker, range(2)))


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class DpdOwnerIntegrityPostgreSQLAcceptanceTests(TransactionTestCase):
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
        statuses = sorted(self._race(lambda _: self._post("2026-07-01")))

        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.monitoring.models import DpdStatus

        self.fixture.account.refresh_from_db()
        row = DpdStatus.objects.get()
        self.assertEqual(statuses, [200, 200])
        self.assertEqual(
            AuditLog.objects.filter(action="monitoring.dpd.calculated").count(), 1
        )
        self.assertEqual(self.fixture.account.current_dpd_status_id, row.pk)

    def test_pointer_mutation_paths_reject_dangling_foreign_and_deleted_snapshots(self):
        from uuid import uuid4

        from django.db import IntegrityError, transaction

        from sfpcl_credit.monitoring.models import DpdStatus
        from sfpcl_credit.tests.servicing_builders import clone_servicing_account

        self.assertEqual(self._post("2026-07-01"), 200)
        snapshot = DpdStatus.objects.get()
        other = clone_servicing_account(fixture=self.fixture, suffix="dpd-pg-other")

        with self.assertRaises(IntegrityError), transaction.atomic():
            type(other).objects.filter(pk=other.pk).update(
                current_dpd_status_id=uuid4()
            )
        other.current_dpd_status_id = snapshot.pk
        with self.assertRaises(IntegrityError), transaction.atomic():
            other.save(update_fields=["current_dpd_status"])
        with self.assertRaises(IntegrityError), transaction.atomic():
            type(other).objects.bulk_update([other], ["current_dpd_status"])
        with self.assertRaises(IntegrityError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE loan_accounts SET current_dpd_status_id = %s "
                    "WHERE loan_account_id = %s",
                    [str(snapshot.pk), str(other.pk)],
                )
        with self.assertRaises(IntegrityError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM dpd_statuses WHERE dpd_status_id = %s",
                    [str(snapshot.pk)],
                )

    def test_older_and_newer_date_race_keeps_the_newest_current_pointer(self):
        from datetime import date

        from sfpcl_credit.monitoring.models import DpdStatus

        statuses = sorted(
            self._race(
                lambda index: self._post(
                    "2026-07-01" if index == 0 else "2026-07-31"
                )
            )
        )

        self.assertEqual(statuses, [200, 200])
        self.assertEqual(DpdStatus.objects.count(), 2)
        self.fixture.account.refresh_from_db()
        self.assertEqual(
            DpdStatus.objects.get(pk=self.fixture.account.current_dpd_status_id).as_of_date,
            date(2026, 7, 31),
        )

    def test_bounded_portfolio_race_retains_one_snapshot_per_identity(self):
        from datetime import date

        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.monitoring.models import DpdStatus
        from sfpcl_credit.tests.servicing_builders import clone_servicing_account

        accounts = [self.fixture.account]
        for index in range(2):
            account = clone_servicing_account(
                fixture=self.fixture,
                suffix=f"dpd-pg-portfolio-{index}",
            )
            RepaymentSchedule.objects.create(
                loan_account=account,
                installment_number=1,
                due_date=date(2026, 6, 30),
                principal_due="1000.00",
                interest_due="100.00",
                charges_due="0.00",
                total_due="1100.00",
                schedule_status="pending",
            )
            accounts.append(account)
        account_ids = [str(account.pk) for account in accounts]

        def submit(_):
            return Client().post(
                "/api/v1/dpd-statuses/bulk-calculate/",
                data=json.dumps(
                    {
                        "as_of_date": "2026-07-01",
                        "loan_account_ids": account_ids,
                        "include_all_active_loans": False,
                    }
                ),
                content_type="application/json",
                **self.fixture.auth,
            ).status_code

        self.assertEqual(sorted(self._race(submit)), [200, 200])
        self.assertEqual(DpdStatus.objects.count(), 3)
        for account in accounts:
            account.refresh_from_db()
            self.assertEqual(
                DpdStatus.objects.get(pk=account.current_dpd_status_id).loan_account_id,
                account.pk,
            )

    def test_failed_policy_race_leaves_history_and_pointer_empty(self):
        from datetime import date

        from sfpcl_credit.monitoring.models import DpdOperationalBucketScheme, DpdStatus

        for version in ("DPD-PG-OVERLAP-1", "DPD-PG-OVERLAP-2"):
            DpdOperationalBucketScheme.objects.create(
                version=version,
                effective_from=date(2026, 1, 1),
            )

        self.assertEqual(
            sorted(self._race(lambda _: self._post("2026-07-01"))),
            [409, 409],
        )
        self.assertEqual(DpdStatus.objects.count(), 0)
        self.fixture.account.refresh_from_db()
        self.assertIsNone(self.fixture.account.current_dpd_status_id)

    def _post(self, as_of_date):
        return Client().post(
            f"/api/v1/loan-accounts/{self.fixture.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": as_of_date}),
            content_type="application/json",
            **self.fixture.auth,
        ).status_code

    @staticmethod
    def _race(submit):
        barrier = Barrier(2)

        def worker(index):
            close_old_connections()
            try:
                barrier.wait(timeout=15)
                return submit(index)
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            return list(pool.map(worker, range(2)))


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class ReminderQueuePostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = ReminderQueueApiTests(
            "test_quarter_end_run_creates_only_beyond_one_year_and_replay_is_zero_write"
        )
        fixture.setUp()
        fixture._make_eligible()
        self.fixture = fixture

    def test_concurrent_quarter_runs_retain_one_reminder_and_delivery_job(self):
        barrier = Barrier(2)

        def submit(_):
            close_old_connections()
            try:
                barrier.wait(timeout=15)
                return Client().post(
                    "/api/v1/reminders/quarter-end-runs/",
                    data=json.dumps(
                        {
                            "quarter_end_date": "2026-06-30",
                            "channel": "sms",
                            "content_template_id": str(self.fixture.sms_template.pk),
                        }
                    ),
                    content_type="application/json",
                    **self.fixture.auth,
                ).status_code
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = sorted(pool.map(submit, range(2)))

        from sfpcl_credit.communications.models import (
            Communication,
            CommunicationDeliveryJob,
        )
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.monitoring.models import Reminder

        self.assertEqual(statuses, [200, 200])
        self.assertEqual(Reminder.objects.count(), 1)
        self.assertEqual(
            Communication.objects.filter(
                related_entity_type="monitoring_reminder"
            ).count(),
            1,
        )
        self.assertEqual(CommunicationDeliveryJob.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="monitoring.reminder.created").count(), 1
        )

    def test_concurrent_exact_send_replay_retains_one_delivery_job(self):
        created = Client().post(
            f"/api/v1/loan-accounts/{self.fixture.account.pk}/reminders/",
            data=json.dumps(
                {
                    "quarter_end_date": "2026-06-30",
                    "reminder_type": "outstanding_beyond_one_year",
                    "channel": "sms",
                    "content_template_id": str(self.fixture.sms_template.pk),
                    "message_body": "Loan remains outstanding at quarter end.",
                    "send_now": False,
                }
            ),
            content_type="application/json",
            **self.fixture.auth,
        )
        self.assertEqual(created.status_code, 200, created.content)
        reminder_id = created.json()["data"]["reminder_id"]
        barrier = Barrier(2)

        def submit(_):
            close_old_connections()
            try:
                barrier.wait(timeout=15)
                return Client().post(
                    f"/api/v1/reminders/{reminder_id}/send/",
                    data=json.dumps({}),
                    content_type="application/json",
                    HTTP_IDEMPOTENCY_KEY="postgres-reminder-send-replay",
                    **self.fixture.auth,
                ).status_code
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = sorted(pool.map(submit, range(2)))

        from sfpcl_credit.communications.models import CommunicationDeliveryJob

        self.assertEqual(statuses, [200, 200])
        self.assertEqual(CommunicationDeliveryJob.objects.count(), 1)


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class ReminderDeliveryIntegrityPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = ReminderQueueApiTests(
            "test_quarter_end_run_creates_only_beyond_one_year_and_replay_is_zero_write"
        )
        fixture.setUp()
        self.fixture = fixture

    def test_calendar_matrix_retains_approved_quarter_decisions(self):
        from datetime import date

        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.monitoring.models import Reminder
        from sfpcl_credit.tests.servicing_builders import clone_servicing_account

        accounts = [self.fixture.account]
        for suffix in ("reminder-calendar-on", "reminder-calendar-after"):
            accounts.append(clone_servicing_account(fixture=self.fixture, suffix=suffix))
        due_dates = [date(2023, 7, 1), date(2023, 6, 30), date(2023, 6, 29)]
        for account, due_date in zip(accounts, due_dates, strict=True):
            RepaymentSchedule.objects.create(
                loan_account=account,
                installment_number=1,
                due_date=due_date,
                principal_due="1000.00",
                interest_due="100.00",
                charges_due="0.00",
                total_due="1100.00",
                schedule_status="pending",
            )
            self.assertEqual(self._post_dpd(account, "2024-06-30"), 200)

        response = self.fixture._run_quarter("2024-06-30")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["data"]["created_count"], 2)
        self.assertEqual(response.json()["data"]["skipped_count"], 1)
        self.assertEqual(Reminder.objects.count(), 2)
        self.assertEqual(
            {row.eligibility_decision_json["boundary_position"] for row in Reminder.objects.all()},
            {"on", "after"},
        )
        for row in Reminder.objects.all():
            self.assertEqual(
                row.eligibility_decision_json["sop_policy_version"],
                "SFPCL-SOP-DPD-1",
            )

    def test_advanced_snapshot_preserves_send_and_repayment_cancels(self):
        self.fixture.test_newer_still_overdue_snapshot_preserves_retained_quarter_send()

    def test_exact_changed_cross_reminder_and_competing_send_integrity(self):
        from datetime import date

        from sfpcl_credit.communications.adapters import FakeSmsDeliveryAdapter
        from sfpcl_credit.communications.models import CommunicationDeliveryJob
        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.processes.communication_delivery import execute_communication_job
        from sfpcl_credit.tests.servicing_builders import clone_servicing_account

        other = clone_servicing_account(fixture=self.fixture, suffix="reminder-cross-key")
        for account in (self.fixture.account, other):
            RepaymentSchedule.objects.create(
                loan_account=account,
                installment_number=1,
                due_date=date(2025, 6, 29),
                principal_due="1000.00",
                interest_due="100.00",
                charges_due="0.00",
                total_due="1100.00",
                schedule_status="pending",
            )
            self.assertEqual(self._post_dpd(account, "2026-06-30"), 200)
        first_id = self._create_unsent(self.fixture.account)
        second_id = self._create_unsent(other)
        barrier = Barrier(2)

        def submit(_):
            close_old_connections()
            try:
                barrier.wait(timeout=15)
                return Client().post(
                    f"/api/v1/reminders/{first_id}/send/",
                    data=json.dumps({}),
                    content_type="application/json",
                    HTTP_IDEMPOTENCY_KEY="pg-reminder-competing-send",
                    **self.fixture.auth,
                ).status_code
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sorted(pool.map(submit, range(2))), [200, 200])
        changed = Client().post(
            f"/api/v1/reminders/{first_id}/send/",
            data=json.dumps({}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="pg-reminder-changed-send",
            **self.fixture.auth,
        )
        cross = Client().post(
            f"/api/v1/reminders/{second_id}/send/",
            data=json.dumps({}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="pg-reminder-competing-send",
            **self.fixture.auth,
        )
        self.assertEqual(changed.status_code, 409, changed.content)
        self.assertEqual(cross.status_code, 409, cross.content)
        self.assertEqual(CommunicationDeliveryJob.objects.count(), 1)
        job = CommunicationDeliveryJob.objects.get()
        self.assertEqual(
            execute_communication_job(job.pk, adapter=FakeSmsDeliveryAdapter())[
                "delivery_status"
            ],
            "sent",
        )
        replay = Client().post(
            f"/api/v1/reminders/{first_id}/send/",
            data=json.dumps({}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="pg-reminder-competing-send",
            **self.fixture.auth,
        )
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(CommunicationDeliveryJob.objects.count(), 1)

    def test_mixed_portfolio_discloses_created_omitted_and_failed_rows(self):
        self.fixture.test_mixed_batch_retains_success_and_discloses_late_contact_failure()

    def test_provider_execution_rechecks_serviceability_and_reverse_consumers(self):
        self.fixture.test_worker_cancels_repaid_reminder_before_provider_execution()

    def _post_dpd(self, account, as_of_date):
        return Client().post(
            f"/api/v1/loan-accounts/{account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": as_of_date}),
            content_type="application/json",
            **self.fixture.auth,
        ).status_code

    def _create_unsent(self, account):
        response = Client().post(
            f"/api/v1/loan-accounts/{account.pk}/reminders/",
            data=json.dumps(
                {
                    "quarter_end_date": "2026-06-30",
                    "reminder_type": "outstanding_beyond_one_year",
                    "channel": "sms",
                    "content_template_id": str(self.fixture.sms_template.pk),
                    "message_body": "Loan remains outstanding at quarter end.",
                    "send_now": False,
                }
            ),
            content_type="application/json",
            **self.fixture.auth,
        )
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()["data"]["reminder_id"]


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


@override_settings(
    DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-quarterly-mis-pg-tests-")
)
@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class QuarterlyMisPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = QuarterlyMisApiTests(
            "test_generate_freezes_cutoff_totals_and_exact_replay"
        )
        fixture.setUp()
        self.fixture = fixture
        calculated = Client().post(
            f"/api/v1/loan-accounts/{fixture.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2026-06-30"}),
            content_type="application/json",
            **fixture.auth,
        )
        self.assertEqual(calculated.status_code, 200, calculated.content)
        from sfpcl_credit.documents.models import DocumentFile

        self.document_count_before = DocumentFile.objects.count()

    def test_concurrent_generation_replays_one_authoritative_report(self):
        barrier = Barrier(2)

        def contender(_index):
            close_old_connections()
            barrier.wait(timeout=15)
            response = Client().post(
                "/api/v1/quarterly-mis-reports/generate/",
                data=json.dumps(
                    {
                        "financial_year": "FY2026-27",
                        "quarter": "Q1",
                        "as_of_date": "2026-06-30",
                    }
                ),
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="quarterly-mis-pg-generate",
                **self.fixture.auth,
            )
            result = (response.status_code, response.json())
            close_old_connections()
            return result

        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(contender, range(2)))

        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.monitoring.models import PortfolioSnapshot, QuarterlyMisReport

        self.assertEqual([status for status, _body in outcomes], [200, 200])
        self.assertEqual(
            len({body["data"]["quarterly_mis_report_id"] for _status, body in outcomes}),
            1,
        )
        self.assertEqual(QuarterlyMisReport.objects.count(), 1)
        self.assertEqual(PortfolioSnapshot.objects.count(), 1)
        self.assertEqual(DocumentFile.objects.count(), self.document_count_before + 2)
        self.assertEqual(AuditLog.objects.filter(action="monitoring.mis.generated").count(), 1)

    def test_concurrent_cfo_review_retains_one_terminal_transition(self):
        generated = self.fixture._generate()
        self.assertEqual(generated.status_code, 200, generated.content)
        report_id = generated.json()["data"]["quarterly_mis_report_id"]
        cfo = self.fixture.identity_fixture._user("cfo", "MIS Race CFO")
        for code in ("finance.loan_account.read", "monitoring.mis.review"):
            self.fixture.identity_fixture._grant(cfo, code)
        cfo_auth = self.fixture.auth_fixture._auth(cfo)
        submitted = Client().post(
            f"/api/v1/quarterly-mis-reports/{report_id}/submit-to-cfo/",
            data=json.dumps({"submitted_to_user_id": str(cfo.pk)}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="quarterly-mis-pg-submit",
            **self.fixture.auth,
        )
        self.assertEqual(submitted.status_code, 200, submitted.content)
        barrier = Barrier(2)

        def contender(_index):
            close_old_connections()
            barrier.wait(timeout=15)
            response = Client().post(
                f"/api/v1/quarterly-mis-reports/{report_id}/mark-reviewed/",
                data="{}",
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY=f"quarterly-mis-pg-review-{_index}",
                **cfo_auth,
            )
            status = response.status_code
            close_old_connections()
            return status

        with ThreadPoolExecutor(max_workers=2) as pool:
            statuses = sorted(pool.map(contender, range(2)))

        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.monitoring.models import QuarterlyMisReport

        self.assertEqual(statuses, [200, 409])
        report = QuarterlyMisReport.objects.get(pk=report_id)
        self.assertEqual(report.status, QuarterlyMisReport.STATUS_REVIEWED)
        self.assertEqual(report.reviewed_by_user_id, cfo.pk)
        self.assertEqual(AuditLog.objects.filter(action="monitoring.mis.reviewed").count(), 1)
