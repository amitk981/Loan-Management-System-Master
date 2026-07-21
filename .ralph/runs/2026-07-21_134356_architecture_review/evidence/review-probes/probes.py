import json
import sys
import unittest
from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

import django
from django.db.models import F
from django.test import SimpleTestCase, TestCase
from django.test.runner import DiscoverRunner


class ReminderDeliveryGapProbe(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_reminder_queue_api import ReminderQueueApiTests

        fixture = ReminderQueueApiTests(
            "test_electronic_send_uses_worker_and_projects_provider_accepted_truth"
        )
        fixture.setUp()
        fixture._make_eligible()
        self.fixture = fixture

    def test_repayment_after_check_but_before_adapter_prevents_provider_call(self):
        from sfpcl_credit.communications.adapters import FakeSmsDeliveryAdapter
        from sfpcl_credit.communications.models import CommunicationDeliveryJob
        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.monitoring.models import Reminder
        from sfpcl_credit.monitoring.modules.reminder_engine import ReminderEngine
        from sfpcl_credit.processes.communication_delivery import execute_communication_job

        fixture = self.fixture
        created = fixture.client.post(
            f"/api/v1/loan-accounts/{fixture.account.pk}/reminders/",
            data=json.dumps(
                {
                    "quarter_end_date": "2026-06-30",
                    "reminder_type": "outstanding_beyond_one_year",
                    "channel": "sms",
                    "content_template_id": str(fixture.sms_template.pk),
                    "message_body": "Loan remains outstanding at quarter end.",
                    "send_now": False,
                }
            ),
            content_type="application/json",
            **fixture.auth,
        )
        self.assertEqual(created.status_code, 200, created.content)
        reminder_id = created.json()["data"]["reminder_id"]
        queued = fixture.client.post(
            f"/api/v1/reminders/{reminder_id}/send/",
            data="{}",
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="review-reminder-check-send-gap",
            **fixture.auth,
        )
        self.assertEqual(queued.status_code, 200, queued.content)
        job = CommunicationDeliveryJob.objects.get(
            communication_id=Reminder.objects.get(pk=reminder_id).communication_id
        )

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


class MisHistoricalInvoiceStatusProbe(SimpleTestCase):
    def test_post_cutoff_invoice_issuance_does_not_rewrite_historical_status(self):
        from sfpcl_credit.monitoring.modules.quarterly_mis import _snapshot_row

        account_id = uuid4()
        invoice = SimpleNamespace(
            pk=uuid4(),
            invoice_date=date(2026, 6, 30),
            invoice_status="issued",
            issued_at=datetime(2026, 7, 2, tzinfo=timezone.utc),
            calculation_version="INV-CALC-1",
        )
        dpd = SimpleNamespace(
            pk=uuid4(),
            days_past_due=366,
            sop_bucket="one_to_two_years",
            total_overdue_amount=Decimal("1100.00"),
            calculation_version="DPD-CALC-1",
        )
        account = SimpleNamespace(
            pk=account_id,
            loan_account_number="LA-REVIEW-ASOF",
            loan_application_id=uuid4(),
            member_id=uuid4(),
            sanction_decision_id=uuid4(),
            loan_application=SimpleNamespace(
                application_reference_number="APP-REVIEW-ASOF",
                borrower_type="individual_farmer",
                crop_plan_id=None,
            ),
            member=SimpleNamespace(
                display_name="Review Borrower",
                registered_district="Pune",
            ),
            terms=SimpleNamespace(pk=uuid4(), security_details_json={}),
            sanctioned_amount=Decimal("400000.00"),
            disbursed_amount=Decimal("400000.00"),
            interest_outstanding=Decimal("0.00"),
            mis_status_history=[SimpleNamespace(pk=uuid4(), to_status="active")],
            mis_dpd_statuses=[dpd],
            mis_repayment_entries=[],
            mis_reversal_entries=[],
            mis_capitalisation_entries=[],
            mis_reminders=[],
            mis_interest_invoices=[invoice],
            mis_disbursements=[],
        )

        row = _snapshot_row(
            account=account,
            period={
                "period_start": date(2026, 4, 1),
                "as_of_date": date(2026, 6, 30),
            },
        )

        self.assertEqual(row["interest_invoice_status"], "draft")


if __name__ == "__main__":
    django.setup()
    selected = sys.argv[1]
    case = globals()[selected]
    runner = DiscoverRunner(verbosity=2, interactive=False)
    runner.setup_test_environment()
    old_config = runner.setup_databases()
    try:
        result = runner.run_suite(unittest.defaultTestLoader.loadTestsFromTestCase(case))
    finally:
        runner.teardown_databases(old_config)
        runner.teardown_test_environment()
    raise SystemExit(0 if result.wasSuccessful() else 1)
