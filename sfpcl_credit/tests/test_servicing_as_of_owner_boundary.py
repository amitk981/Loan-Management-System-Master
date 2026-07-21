import json
import tempfile
from datetime import date

from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.db.models import F
from django.test import Client, TestCase, override_settings


class ServicingAsOfOwnerBoundaryAssertions:
    def _assert_dpd_database_and_policy_owner(self):
        from sfpcl_credit.monitoring.models import DpdOperationalBucketScheme, DpdStatus
        from sfpcl_credit.tests.servicing_builders import clone_servicing_account
        from sfpcl_credit.tests.test_servicing_postgresql_acceptance import (
            DpdOwnerIntegrityPostgreSQLAcceptanceTests,
        )

        fixture = DpdOwnerIntegrityPostgreSQLAcceptanceTests(
            "test_same_date_race_retains_one_snapshot_audit_and_current_pointer"
        )
        fixture.setUp()
        self.assertEqual(fixture._post("2026-07-01"), 200)
        snapshot = DpdStatus.objects.get()
        other = clone_servicing_account(fixture=fixture.fixture, suffix="asof-reparent")
        with self.assertRaises(IntegrityError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE dpd_statuses SET loan_account_id = %s WHERE dpd_status_id = %s",
                    [
                        other.pk.hex if connection.vendor == "sqlite" else str(other.pk),
                        snapshot.pk.hex if connection.vendor == "sqlite" else str(snapshot.pk),
                    ],
                )
        scheme = DpdOperationalBucketScheme.objects.create(
            version="ASOF-DPD-POLICY-1", effective_from=date(2026, 1, 1)
        )
        with self.assertRaises(ValidationError):
            DpdOperationalBucketScheme.objects.filter(pk=scheme.pk).update(
                version="ASOF-DPD-POLICY-EDITED"
            )

    def _assert_capitalisation_is_classified_once(self):
        from sfpcl_credit.identity.models import Permission, RolePermission
        from sfpcl_credit.tests.servicing_builders import build_interest_capitalisation_fixture

        fixture = build_interest_capitalisation_fixture()
        capitalised = fixture.submit(idempotency_key="asof-dpd-capitalisation")
        self.assertEqual(capitalised.status_code, 200, capitalised.content)
        for code in ("monitoring.dpd.calculate", "monitoring.dpd.read"):
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={"permission_name": code, "module_name": "monitoring", "risk_level": "high"},
            )
            RolePermission.objects.get_or_create(role=fixture.actor.primary_role, permission=permission)
        response = Client().post(
            f"/api/v1/loan-accounts/{fixture.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2027-05-01"}),
            content_type="application/json",
            **fixture.auth,
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["data"]["interest_overdue_amount"], "0.00")

    def _reminder_fixture(self):
        from sfpcl_credit.tests.test_reminder_queue_api import ReminderQueueApiTests

        fixture = ReminderQueueApiTests(
            "test_electronic_send_uses_worker_and_projects_provider_accepted_truth"
        )
        fixture.setUp()
        fixture._make_eligible()
        created = fixture.client.post(
            f"/api/v1/loan-accounts/{fixture.account.pk}/reminders/",
            data=json.dumps({
                "quarter_end_date": "2026-06-30",
                "reminder_type": "outstanding_beyond_one_year",
                "channel": "sms",
                "content_template_id": str(fixture.sms_template.pk),
                "message_body": "Loan remains outstanding at quarter end.",
                "send_now": False,
            }),
            content_type="application/json",
            **fixture.auth,
        )
        return fixture, created.json()["data"]["reminder_id"]

    def _assert_reminder_provider_boundary(self):
        from sfpcl_credit.communications.adapters import FakeSmsDeliveryAdapter
        from sfpcl_credit.communications.models import CommunicationDeliveryJob
        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.monitoring.models import Reminder
        from sfpcl_credit.processes.communication_delivery import execute_communication_job

        fixture, reminder_id = self._reminder_fixture()
        queued = fixture.client.post(
            f"/api/v1/reminders/{reminder_id}/send/", data="{}",
            content_type="application/json", HTTP_IDEMPOTENCY_KEY="asof-reminder-send", **fixture.auth,
        )
        self.assertEqual(queued.status_code, 200, queued.content)
        RepaymentSchedule.objects.filter(loan_account=fixture.account).update(
            paid_principal=F("principal_due"), paid_interest=F("interest_due"),
            paid_charges=F("charges_due"), schedule_status="paid",
        )
        job = CommunicationDeliveryJob.objects.get(
            communication_id=Reminder.objects.get(pk=reminder_id).communication_id
        )
        adapter = FakeSmsDeliveryAdapter()
        result = execute_communication_job(job.pk, adapter=adapter)
        self.assertEqual(result["delivery_status"], "cancelled")

    def _mis_fixture(self):
        from sfpcl_credit.tests.test_quarterly_mis_api import QuarterlyMisApiTests

        fixture = QuarterlyMisApiTests("test_generate_freezes_cutoff_totals_and_exact_replay")
        fixture.setUp()
        calculated = fixture.client.post(
            f"/api/v1/loan-accounts/{fixture.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2026-06-30"}), content_type="application/json", **fixture.auth,
        )
        self.assertEqual(calculated.status_code, 200, calculated.content)
        return fixture

    def _assert_mis_replay_and_cutoff_owner(self):
        from django.utils import timezone
        from sfpcl_credit.identity.models import Permission, RolePermission
        from sfpcl_credit.monitoring.models import DpdStatus, Reminder

        fixture = self._mis_fixture()
        dpd = DpdStatus.objects.get(loan_account=fixture.account)
        Reminder.objects.create(
            loan_account=fixture.account, loan_application=fixture.account.loan_application,
            member=fixture.account.member, dpd_status=dpd, quarter_end_date=date(2026, 6, 30),
            eligibility_decision_json={"eligible": True},
            reminder_type=Reminder.TYPE_OUTSTANDING_BEYOND_ONE_YEAR,
            origin=Reminder.ORIGIN_MANUAL, channel=Reminder.CHANNEL_PHONE,
            message_body="Late reminder", delivery_status=Reminder.STATUS_CALL_LOGGED,
            contacted_person="borrower", call_outcome="late", created_by_user=fixture.actor,
            sent_at=timezone.now(),
        )
        report = fixture._generate(key="asof-mis-late-reminder")
        self.assertEqual(report.status_code, 200, report.content)
        self.assertEqual(report.json()["data"]["totals"]["reminders_count"], 0)
        permission = Permission.objects.get(permission_code="finance.loan_account.read")
        RolePermission.objects.filter(role=fixture.actor.primary_role, permission=permission).delete()
        self.assertEqual(
            fixture._generate(key="asof-mis-late-reminder").status_code, 403
        )

    def _assert_batch_continuation_contract(self):
        fixture, _reminder_id = self._reminder_fixture()
        response = fixture.client.post(
            "/api/v1/reminders/quarter-end-runs/",
            data=json.dumps({
                "quarter_end_date": "2026-06-30", "channel": "sms",
                "content_template_id": str(fixture.sms_template.pk),
            }),
            content_type="application/json", **fixture.auth,
        )
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["processed_count"], len(data["results"]))
        self.assertIn("truncated", data)
        self.assertIn("continuation_after_loan_account_id", data)


@override_settings(DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-asof-owner-"))
class ServicingAsOfOwnerBoundaryTests(ServicingAsOfOwnerBoundaryAssertions, TestCase):
    def test_dpd_database_and_policy_owner(self):
        self._assert_dpd_database_and_policy_owner()

    def test_capitalisation_is_classified_once(self):
        self._assert_capitalisation_is_classified_once()

    def test_reminder_provider_boundary_rechecks_serviceability(self):
        self._assert_reminder_provider_boundary()

    def test_mis_replay_and_cutoff_owner(self):
        self._assert_mis_replay_and_cutoff_owner()

    def test_batch_continuation_contract(self):
        self._assert_batch_continuation_contract()
