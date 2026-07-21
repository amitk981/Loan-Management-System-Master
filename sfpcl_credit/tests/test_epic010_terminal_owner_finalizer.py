"""Permanent regressions for the Epic 010 terminal servicing owners."""

import json
import csv
import io
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from tempfile import TemporaryDirectory
from datetime import date, datetime, timezone as datetime_timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from django.db.models import F
from django.db import close_old_connections, connection
from django.test import SimpleTestCase, TestCase, TransactionTestCase, override_settings


class Epic010ReminderOwnerRegressionTests(TransactionTestCase):
    def setUp(self):
        from sfpcl_credit.tests.servicing_builders import build_terminal_reminder_fixture

        self.storage = TemporaryDirectory()
        self.storage_settings = override_settings(DOCUMENT_STORAGE_ROOT=self.storage.name)
        self.storage_settings.enable()
        self.fixture = build_terminal_reminder_fixture(suffix=self._testMethodName[-24:])

    def tearDown(self):
        self.storage_settings.disable()
        self.storage.cleanup()
        super().tearDown()

    def test_repayment_after_check_but_before_adapter_prevents_provider_call(self):
        from sfpcl_credit.communications.adapters import FakeSmsDeliveryAdapter
        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.monitoring.modules.reminder_engine import ReminderEngine
        from sfpcl_credit.processes.communication_delivery import execute_communication_job

        fixture = self.fixture
        job = fixture.queue(idempotency_key="terminal-reminder-check-send-gap")

        class CountingAdapter(FakeSmsDeliveryAdapter):
            calls = 0

            def send_sms(self, payload, idempotency_key):
                self.calls += 1
                return super().send_sms(payload, idempotency_key)

        original_check = ReminderEngine.cancel_unserviceable_delivery

        def repayment_wins_after_check(*, communication_job_id):
            result = original_check(communication_job_id=communication_job_id)
            self.assertIsNone(result)
            RepaymentSchedule.objects.filter(loan_account=fixture.account).update(
                paid_principal=F("principal_due"),
                paid_interest=F("interest_due"),
                paid_charges=F("charges_due"),
                schedule_status="paid",
            )
            return result

        adapter = CountingAdapter()
        with patch.object(
            ReminderEngine,
            "cancel_unserviceable_delivery",
            side_effect=repayment_wins_after_check,
        ):
            result = execute_communication_job(job.pk, adapter=adapter)

        self.assertEqual(adapter.calls, 0)
        self.assertEqual(result["delivery_status"], "cancelled")


class Epic010TerminalOwnerFinalizerPostgreSQLAcceptanceTests(
    Epic010ReminderOwnerRegressionTests
):
    def test_recipient_source_change_cancels_before_provider(self):
        from sfpcl_credit.communications.adapters import FakeSmsDeliveryAdapter
        from sfpcl_credit.identity.models import RolePermission
        from sfpcl_credit.processes.communication_delivery import execute_communication_job

        job = self.fixture.queue(idempotency_key="terminal-source-change")
        self.fixture.account.member.mobile_number = "+919999999999"
        self.fixture.account.member.save(update_fields=["mobile_number"])
        RolePermission.objects.filter(
            role=self.fixture.actor.primary_role,
            permission__permission_code="finance.loan_account.read",
        ).delete()
        adapter = FakeSmsDeliveryAdapter()

        result = execute_communication_job(job.pk, adapter=adapter)

        self.assertEqual(result["delivery_status"], "cancelled")

    def test_competing_workers_retain_one_provider_effect(self):
        from sfpcl_credit.communications.adapters import FakeSmsDeliveryAdapter
        from sfpcl_credit.processes.communication_delivery import execute_communication_job

        class CountingAdapter(FakeSmsDeliveryAdapter):
            calls = 0

            def send_sms(self, payload, idempotency_key):
                self.calls += 1
                return super().send_sms(payload, idempotency_key)

        job = self.fixture.queue(idempotency_key="terminal-workers")
        adapter = CountingAdapter()
        if connection.vendor == "postgresql":
            barrier = Barrier(2)

            def contender():
                close_old_connections()
                barrier.wait()
                try:
                    return execute_communication_job(job.pk, adapter=adapter)
                finally:
                    close_old_connections()

            with ThreadPoolExecutor(max_workers=2) as executor:
                first, replay = list(executor.map(lambda _index: contender(), range(2)))
        else:
            first = execute_communication_job(job.pk, adapter=adapter)
            replay = execute_communication_job(job.pk, adapter=adapter)

        self.assertEqual(adapter.calls, 1)
        self.assertEqual(first["delivery_status"], "sent")
        self.assertEqual(replay["delivery_status"], "sent")

    def test_exact_worker_retry_reuses_provider_identity(self):
        from sfpcl_credit.communications.adapters import FakeSmsDeliveryAdapter
        from sfpcl_credit.processes.communication_delivery import execute_communication_job

        class CountingAdapter(FakeSmsDeliveryAdapter):
            calls = 0

            def send_sms(self, payload, idempotency_key):
                self.calls += 1
                return super().send_sms(payload, idempotency_key)

        job = self.fixture.queue(idempotency_key="terminal-retry")
        adapter = CountingAdapter()
        execute_communication_job(job.pk, adapter=adapter)
        execute_communication_job(job.pk, adapter=adapter)
        self.assertEqual(adapter.calls, 1)

    def test_provider_timeout_then_repayment_prevents_retry_effect(self):
        from sfpcl_credit.communications.adapters import FakeSmsDeliveryAdapter
        from sfpcl_credit.communications.models import CommunicationDeliveryJob
        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.processes.communication_delivery import execute_communication_job
        from django.utils import timezone

        class TimeoutAdapter(FakeSmsDeliveryAdapter):
            calls = 0

            def send_sms(self, payload, idempotency_key):
                self.calls += 1
                raise TimeoutError

        class CountingAdapter(FakeSmsDeliveryAdapter):
            calls = 0

            def send_sms(self, payload, idempotency_key):
                self.calls += 1
                return super().send_sms(payload, idempotency_key)

        job = self.fixture.queue(idempotency_key="terminal-timeout")
        timeout = TimeoutAdapter()
        execute_communication_job(job.pk, adapter=timeout)
        CommunicationDeliveryJob.objects.filter(pk=job.pk).update(
            next_attempt_at=timezone.now()
        )
        RepaymentSchedule.objects.filter(loan_account=self.fixture.account).update(
            paid_principal=F("principal_due"),
            paid_interest=F("interest_due"),
            paid_charges=F("charges_due"),
            schedule_status="paid",
        )
        retry = CountingAdapter()
        result = execute_communication_job(job.pk, adapter=retry)

        self.assertEqual(timeout.calls, 1)
        self.assertEqual(retry.calls, 0)
        self.assertEqual(result["delivery_status"], "cancelled")


class Epic010MisOwnerRegressionTests(SimpleTestCase):
    def test_post_cutoff_invoice_issuance_does_not_rewrite_historical_status(self):
        from sfpcl_credit.monitoring.modules.quarterly_mis import _snapshot_row

        invoice = SimpleNamespace(
            pk=uuid4(),
            invoice_date=date(2026, 6, 30),
            invoice_status="issued",
            generated_at=datetime(2026, 6, 29, tzinfo=datetime_timezone.utc),
            issued_at=datetime(2026, 7, 2, tzinfo=datetime_timezone.utc),
            calculation_version="INV-CALC-1",
        )
        account = SimpleNamespace(
            pk=uuid4(),
            loan_account_number="LA-TERMINAL-ASOF",
            loan_application_id=uuid4(),
            member_id=uuid4(),
            sanction_decision_id=uuid4(),
            loan_application=SimpleNamespace(
                application_reference_number="APP-TERMINAL-ASOF",
                borrower_type="individual_farmer",
                crop_plan_id=None,
            ),
            member=SimpleNamespace(display_name="Synthetic Borrower", registered_district="Pune"),
            terms=SimpleNamespace(pk=uuid4(), security_details_json={}),
            sanctioned_amount=Decimal("400000.00"),
            disbursed_amount=Decimal("400000.00"),
            interest_outstanding=Decimal("0.00"),
            mis_status_history=[SimpleNamespace(pk=uuid4(), to_status="active")],
            mis_dpd_statuses=[
                SimpleNamespace(
                    pk=uuid4(),
                    days_past_due=366,
                    sop_bucket="one_to_two_years",
                    total_overdue_amount=Decimal("1100.00"),
                    calculation_version="DPD-CALC-1",
                )
            ],
            mis_repayment_entries=[],
            mis_reversal_entries=[],
            mis_capitalisation_entries=[],
            mis_reminders=[],
            mis_interest_invoices=[invoice],
            mis_disbursements=[],
        )

        row = _snapshot_row(
            account=account,
            period={"period_start": date(2026, 4, 1), "as_of_date": date(2026, 6, 30)},
        )

        self.assertEqual(row["interest_invoice_status"], "draft")

    def test_real_invoice_model_projects_before_on_and_after_cutoff_lifecycle(self):
        from sfpcl_credit.interest.models import InterestInvoice
        from sfpcl_credit.monitoring.modules.quarterly_mis import (
            _invoice_status_at_cutoff,
        )

        cutoff = date(2026, 6, 30)
        cases = (
            (
                InterestInvoice(
                    generated_at=datetime(2026, 6, 29, tzinfo=datetime_timezone.utc),
                    issued_at=None,
                    invoice_status="draft",
                ),
                "draft",
            ),
            (
                InterestInvoice(
                    generated_at=datetime(2026, 6, 30, tzinfo=datetime_timezone.utc),
                    issued_at=datetime(2026, 6, 30, tzinfo=datetime_timezone.utc),
                    invoice_status="issued",
                ),
                "issued",
            ),
            (
                InterestInvoice(
                    generated_at=datetime(2026, 7, 1, tzinfo=datetime_timezone.utc),
                    issued_at=None,
                    invoice_status="draft",
                ),
                "not_generated",
            ),
        )
        for invoice, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(
                    _invoice_status_at_cutoff(invoice=invoice, cutoff=cutoff),
                    expected,
                )


class Epic010StatementOwnerRegressionTests(SimpleTestCase):
    def test_empty_borrower_csv_retains_safe_metadata_without_internal_fields(self):
        from sfpcl_credit.processes.loan_ledger_statements import _render_csv

        statement = {
            "statement_job_id": "internal-job",
            "loan_account_id": "internal-account",
            "format": "csv",
            "from_date": "2026-04-01",
            "to_date": "2026-06-30",
            "as_of_date": "2026-06-30",
            "generated_at": "2026-07-01T00:00:00Z",
            "opening_balance": "400000.00",
            "closing_balance": "400000.00",
            "row_count": 0,
            "rows": [],
        }

        body = _render_csv(statement, borrower_safe=True).decode("utf-8")
        rows = list(csv.DictReader(io.StringIO(body)))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["from_date"], "2026-04-01")
        self.assertEqual(rows[0]["closing_balance"], "400000.00")
        for internal in (
            "statement_job_id",
            "loan_account_id",
            "owner_reference",
            "posted_by",
            "sap_status",
            "remarks",
        ):
            self.assertNotIn(internal, rows[0])


class Epic010DirectRepaymentOwnerRegressionTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.servicing_builders import (
            build_terminal_direct_repayment_fixture,
        )

        self.storage = TemporaryDirectory()
        self.storage_settings = override_settings(DOCUMENT_STORAGE_ROOT=self.storage.name)
        self.storage_settings.enable()
        self.fixture = build_terminal_direct_repayment_fixture(
            suffix=self._testMethodName[-24:]
        )
        self.fixture.schedule("400000.00")

    def tearDown(self):
        self.storage_settings.disable()
        self.storage.cleanup()
        super().tearDown()

    def test_exact_command_replay_returns_one_complete_financial_outcome(self):
        payload = {
            "capture": self.fixture.payload(),
            "sap_posting": {
                "sap_entry_reference": "SAP-TERMINAL-001",
                "sap_posted_at": "2026-12-04T10:00:00Z",
                "remarks": "Synthetic SAP receipt confirmation.",
            },
        }
        url = f"/api/v1/loan-accounts/{self.fixture.account.pk}/direct-repayment-command/"

        first = self.fixture.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="terminal-command-001",
            **self.fixture.auth,
        )
        replay = self.fixture.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="terminal-command-001",
            **self.fixture.auth,
        )

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertFalse(first.json()["data"]["replayed"])
        self.assertTrue(replay.json()["data"]["replayed"])
        self.assertEqual(first.json()["data"]["capture"], replay.json()["data"]["capture"])
        self.assertEqual(first.json()["data"]["allocation"], replay.json()["data"]["allocation"])
        self.assertIsNotNone(replay.json()["data"]["allocation"])
