import json
import sys
import tempfile
import unittest
from datetime import date

import django
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.db.models import F
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.test.runner import DiscoverRunner


class DpdSnapshotOwnerProbe(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        from sfpcl_credit.tests.test_servicing_postgresql_acceptance import (
            DpdOwnerIntegrityPostgreSQLAcceptanceTests,
        )

        retained = DpdOwnerIntegrityPostgreSQLAcceptanceTests(
            "test_same_date_race_retains_one_snapshot_audit_and_current_pointer"
        )
        retained.setUp()
        self.retained = retained

    def test_database_rejects_reparenting_the_current_snapshot(self):
        from sfpcl_credit.monitoring.models import DpdStatus
        from sfpcl_credit.tests.servicing_builders import clone_servicing_account

        self.assertEqual(self.retained._post("2026-07-01"), 200)
        snapshot = DpdStatus.objects.get()
        other = clone_servicing_account(
            fixture=self.retained.fixture, suffix="review-dpd-reparent"
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE dpd_statuses SET loan_account_id = %s "
                    "WHERE dpd_status_id = %s",
                    [str(other.pk), str(snapshot.pk)],
                )

    def test_approved_operational_policy_amends_by_new_version(self):
        from sfpcl_credit.monitoring.models import DpdOperationalBucketScheme

        scheme = DpdOperationalBucketScheme.objects.create(
            version="REVIEW-DPD-POLICY-1",
            effective_from=date(2026, 1, 1),
            status="active",
        )
        with self.assertRaises(ValidationError):
            DpdOperationalBucketScheme.objects.filter(pk=scheme.pk).update(
                version="REVIEW-DPD-POLICY-EDITED"
            )


@override_settings(DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="review-dpd-capitalisation-"))
class DpdCapitalisationReverseConsumerProbe(TestCase):
    def test_capitalised_schedule_interest_is_not_reported_overdue_again(self):
        from sfpcl_credit.identity.models import Permission, RolePermission
        from sfpcl_credit.tests.servicing_builders import (
            build_interest_capitalisation_fixture,
        )

        fixture = build_interest_capitalisation_fixture()
        capitalised = fixture.submit(idempotency_key="review-dpd-capitalisation")
        self.assertEqual(capitalised.status_code, 200, capitalised.content)
        for code in ("monitoring.dpd.calculate", "monitoring.dpd.read"):
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "monitoring",
                    "risk_level": "high",
                },
            )
            RolePermission.objects.get_or_create(
                role=fixture.actor.primary_role, permission=permission
            )

        response = Client().post(
            f"/api/v1/loan-accounts/{fixture.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2027-05-01"}),
            content_type="application/json",
            **fixture.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["data"]["interest_overdue_amount"], "0.00")


class ReminderDeliveryOwnerProbe(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_reminder_queue_api import ReminderQueueApiTests

        fixture = ReminderQueueApiTests(
            "test_electronic_send_uses_worker_and_projects_provider_accepted_truth"
        )
        fixture.setUp()
        self.fixture = fixture

    def test_provider_cannot_run_after_current_schedule_truth_becomes_paid(self):
        from sfpcl_credit.communications.adapters import FakeSmsDeliveryAdapter
        from sfpcl_credit.communications.models import CommunicationDeliveryJob
        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.monitoring.models import Reminder
        from sfpcl_credit.processes.communication_delivery import (
            execute_communication_job,
        )

        fixture = self.fixture
        fixture._make_eligible()
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
        reminder_id = created.json()["data"]["reminder_id"]
        queued = fixture.client.post(
            f"/api/v1/reminders/{reminder_id}/send/",
            data="{}",
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="review-reminder-provider-gap",
            **fixture.auth,
        )
        self.assertEqual(queued.status_code, 200, queued.content)
        job = CommunicationDeliveryJob.objects.get(
            communication_id=Reminder.objects.get().communication_id
        )

        class RepaymentWinsBeforeProvider(FakeSmsDeliveryAdapter):
            called = False

            def send_sms(self, payload, idempotency_key):
                self.called = True
                RepaymentSchedule.objects.filter(
                    loan_account=fixture.account
                ).update(
                    paid_principal=F("principal_due"),
                    paid_interest=F("interest_due"),
                    paid_charges=F("charges_due"),
                    schedule_status="paid",
                )
                return super().send_sms(payload, idempotency_key)

        adapter = RepaymentWinsBeforeProvider()
        result = execute_communication_job(job.pk, adapter=adapter)

        self.assertFalse(adapter.called)
        self.assertEqual(result["delivery_status"], "cancelled")


@override_settings(DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="review-quarterly-mis-"))
class QuarterlyMisOwnerProbe(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_quarterly_mis_api import QuarterlyMisApiTests

        fixture = QuarterlyMisApiTests(
            "test_generate_freezes_cutoff_totals_and_exact_replay"
        )
        fixture.setUp()
        self.fixture = fixture
        calculated = fixture.client.post(
            f"/api/v1/loan-accounts/{fixture.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2026-06-30"}),
            content_type="application/json",
            **fixture.auth,
        )
        self.assertEqual(calculated.status_code, 200, calculated.content)

    def test_generation_replay_rechecks_current_portfolio_scope(self):
        from sfpcl_credit.identity.models import Permission, RolePermission

        first = self.fixture._generate()
        self.assertEqual(first.status_code, 200, first.content)
        read_permission = Permission.objects.get(
            permission_code="finance.loan_account.read"
        )
        RolePermission.objects.filter(
            role=self.fixture.actor.primary_role, permission=read_permission
        ).delete()

        replay = self.fixture._generate()

        self.assertEqual(replay.status_code, 403, replay.content)

    def test_late_reminder_does_not_enter_an_as_of_cutoff_snapshot(self):
        from django.utils import timezone
        from sfpcl_credit.monitoring.models import DpdStatus, Reminder

        dpd = DpdStatus.objects.get()
        Reminder.objects.create(
            loan_account=self.fixture.account,
            loan_application=self.fixture.account.loan_application,
            member=self.fixture.account.member,
            dpd_status=dpd,
            quarter_end_date=date(2026, 6, 30),
            eligibility_decision_json={"eligible": True},
            reminder_type=Reminder.TYPE_OUTSTANDING_BEYOND_ONE_YEAR,
            origin=Reminder.ORIGIN_MANUAL,
            channel=Reminder.CHANNEL_PHONE,
            message_body="Late-entered quarter reminder.",
            delivery_status=Reminder.STATUS_CALL_LOGGED,
            contacted_person="borrower",
            call_outcome="Follow-up recorded after cutoff.",
            next_follow_up_date=date(2026, 7, 31),
            created_by_user=self.fixture.actor,
            sent_at=timezone.now(),
        )

        report = self.fixture._generate(key="review-mis-late-reminder")

        self.assertEqual(report.status_code, 200, report.content)
        self.assertEqual(report.json()["data"]["totals"]["reminders_count"], 0)


if __name__ == "__main__":
    django.setup()
    selected = sys.argv[1]
    case = globals()[selected]
    runner = DiscoverRunner(verbosity=1, interactive=False)
    runner.setup_test_environment()
    old_config = runner.setup_databases()
    try:
        result = runner.run_suite(unittest.defaultTestLoader.loadTestsFromTestCase(case))
    finally:
        runner.teardown_databases(old_config)
        runner.teardown_test_environment()
    raise SystemExit(0 if result.wasSuccessful() else 1)
