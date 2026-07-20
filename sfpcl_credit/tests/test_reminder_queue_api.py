import json
from datetime import date

from django.test import Client, TestCase


class ReminderQueueApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.communications.models import ContentTemplate
        from sfpcl_credit.identity.models import Permission, RolePermission
        from sfpcl_credit.tests.test_loan_schedule_ledger_api import (
            LoanScheduleLedgerApiTests,
        )

        fixture = LoanScheduleLedgerApiTests(
            "test_authorised_reader_gets_ordered_decimal_schedule_truth"
        )
        fixture.setUp()
        self.account = fixture.account
        self.actor = fixture.fixture.reader
        self.auth = fixture.auth
        self.client = Client()
        for code in (
            "monitoring.dpd.read",
            "monitoring.dpd.calculate",
            "monitoring.reminder.create",
        ):
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "monitoring",
                    "risk_level": "high",
                },
            )
            RolePermission.objects.get_or_create(
                role=self.actor.primary_role,
                permission=permission,
            )
        self.account.member.mobile_number = "+919876543210"
        self.account.member.email = "synthetic.reminder.borrower@example.test"
        self.account.member.save(update_fields=["mobile_number", "email"])
        self.sms_template = ContentTemplate.objects.create(
            template_code="quarter_end_outstanding_sms",
            template_name="Quarter-end outstanding SMS",
            template_type="sms",
            audience="borrower",
            body_template="Loan {{loan_account_number}} remains outstanding at {{quarter_end_date}}.",
            variables_json=["loan_account_number", "quarter_end_date"],
            approval_status="approved",
            template_version="1",
            effective_from=date(2020, 1, 1),
        )

    def test_quarter_end_run_creates_only_beyond_one_year_and_replay_is_zero_write(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.monitoring.models import Reminder

        RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=date(2025, 6, 29),
            principal_due="1000.00",
            interest_due="100.00",
            charges_due="0.00",
            total_due="1100.00",
            schedule_status="pending",
        )
        calculated = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2026-06-30"}),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(calculated.status_code, 200, calculated.content)

        first = self._run_quarter("2026-06-30")
        replay = self._run_quarter("2026-06-30")

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(first.json()["data"]["created_count"], 1)
        self.assertEqual(replay.json()["data"]["created_count"], 0)
        self.assertEqual(replay.json()["data"]["retained_count"], 1)
        row = Reminder.objects.get()
        self.account.refresh_from_db()
        self.assertEqual(row.loan_account_id, self.account.pk)
        self.assertEqual(row.member_id, self.account.member_id)
        self.assertEqual(row.dpd_status_id, self.account.current_dpd_status_id)
        self.assertEqual(row.quarter_end_date, date(2026, 6, 30))
        self.assertEqual(row.reminder_type, "outstanding_beyond_one_year")
        self.assertEqual(row.origin, "automatic")
        self.assertEqual(row.channel, "sms")
        self.assertEqual(row.delivery_status, "queued")
        self.assertEqual(row.created_by_user_id, self.actor.pk)
        self.assertIsNotNone(row.communication_id)
        self.assertEqual(
            AuditLog.objects.filter(action="monitoring.reminder.created").count(), 1
        )

    def test_day_before_first_anniversary_is_not_eligible(self):
        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.monitoring.models import Reminder

        RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=date(2025, 7, 1),
            principal_due="1000.00",
            interest_due="100.00",
            charges_due="0.00",
            total_due="1100.00",
            schedule_status="pending",
        )
        calculated = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2026-06-30"}),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(calculated.status_code, 200, calculated.content)
        self.assertEqual(calculated.json()["data"]["sop_bucket"], "current")

        response = self._run_quarter("2026-06-30")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["data"]["created_count"], 0)
        self.assertEqual(Reminder.objects.count(), 0)

    def test_phone_log_retains_outcome_and_follow_up_without_provider_communication(self):
        from sfpcl_credit.communications.models import Communication
        from sfpcl_credit.monitoring.models import Reminder

        self._make_eligible()
        before = Communication.objects.count()

        response = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/reminders/",
            data=json.dumps(
                {
                    "quarter_end_date": "2026-06-30",
                    "reminder_type": "outstanding_beyond_one_year",
                    "channel": "phone",
                    "message_body": "Quarter-end repayment follow-up call recorded.",
                    "call_outcome": "Borrower will review the repayment schedule.",
                    "contacted_person": "borrower",
                    "next_follow_up_date": "2026-07-07",
                    "send_now": False,
                }
            ),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        row = Reminder.objects.get()
        self.assertEqual(row.delivery_status, "call_logged")
        self.assertEqual(row.origin, "manual")
        self.assertEqual(row.call_outcome, "Borrower will review the repayment schedule.")
        self.assertEqual(row.contacted_person, "borrower")
        self.assertEqual(row.next_follow_up_date, date(2026, 7, 7))
        self.assertIsNone(row.communication_id)
        self.assertEqual(Communication.objects.count(), before)

        second = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/reminders/",
            data=json.dumps(
                {
                    "quarter_end_date": "2026-06-30",
                    "reminder_type": "outstanding_beyond_one_year",
                    "channel": "phone",
                    "message_body": "Second quarter-end follow-up call recorded.",
                    "call_outcome": "Borrower requested another follow-up.",
                    "contacted_person": "borrower",
                    "next_follow_up_date": "2026-07-14",
                    "send_now": False,
                }
            ),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(second.status_code, 200, second.content)
        self.assertEqual(Reminder.objects.count(), 2)
        self.assertEqual(Communication.objects.count(), before)

    def test_stale_electronic_reminder_is_cancelled_before_send(self):
        from sfpcl_credit.communications.models import CommunicationDeliveryJob
        from sfpcl_credit.monitoring.models import Reminder

        self._make_eligible()
        created = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/reminders/",
            data=json.dumps(
                {
                    "quarter_end_date": "2026-06-30",
                    "reminder_type": "outstanding_beyond_one_year",
                    "channel": "sms",
                    "content_template_id": str(self.sms_template.pk),
                    "message_body": "Loan remains outstanding at quarter end.",
                    "send_now": False,
                }
            ),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(created.status_code, 200, created.content)
        row = Reminder.objects.get()
        self.assertEqual(row.delivery_status, "queued")
        self.assertEqual(CommunicationDeliveryJob.objects.count(), 0)

        self.account.total_outstanding = 0
        self.account.principal_outstanding = 0
        self.account.loan_account_status = "fully_repaid"
        self.account.save(
            update_fields=[
                "total_outstanding",
                "principal_outstanding",
                "loan_account_status",
            ]
        )
        sent = self.client.post(
            f"/api/v1/reminders/{row.pk}/send/",
            data=json.dumps({}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="stale-reminder-send",
            **self.auth,
        )

        self.assertEqual(sent.status_code, 200, sent.content)
        row.refresh_from_db()
        self.assertEqual(row.delivery_status, "cancelled")
        self.assertEqual(row.status_reason, "loan_no_longer_eligible")
        self.assertEqual(row.call_outcome, "")
        self.assertEqual(CommunicationDeliveryJob.objects.count(), 0)

    def test_electronic_send_uses_worker_and_projects_provider_accepted_truth(self):
        from sfpcl_credit.communications.adapters import FakeSmsDeliveryAdapter
        from sfpcl_credit.communications.models import CommunicationDeliveryJob
        from sfpcl_credit.monitoring.models import Reminder
        from sfpcl_credit.processes.communication_delivery import (
            execute_communication_job,
        )

        self._make_eligible()
        created = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/reminders/",
            data=json.dumps(
                {
                    "quarter_end_date": "2026-06-30",
                    "reminder_type": "outstanding_beyond_one_year",
                    "channel": "sms",
                    "content_template_id": str(self.sms_template.pk),
                    "message_body": "Loan remains outstanding at quarter end.",
                    "send_now": False,
                }
            ),
            content_type="application/json",
            **self.auth,
        )
        reminder_id = created.json()["data"]["reminder_id"]
        queued = self.client.post(
            f"/api/v1/reminders/{reminder_id}/send/",
            data=json.dumps({}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="reminder-provider-send",
            **self.auth,
        )
        self.assertEqual(queued.status_code, 200, queued.content)
        self.assertEqual(queued.json()["data"]["delivery_status"], "queued")
        job = CommunicationDeliveryJob.objects.get(
            communication_id=Reminder.objects.get().communication_id
        )

        result = execute_communication_job(job.pk, adapter=FakeSmsDeliveryAdapter())
        replay = self.client.post(
            f"/api/v1/reminders/{reminder_id}/send/",
            data=json.dumps({}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="reminder-provider-send",
            **self.auth,
        )

        self.assertEqual(result["delivery_status"], "sent")
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"]["delivery_status"], "sent")

    def test_permission_contact_and_template_fail_closed_without_reminder(self):
        from sfpcl_credit.communications.models import Communication
        from sfpcl_credit.identity.models import Permission, RolePermission
        from sfpcl_credit.monitoring.models import Reminder

        self._make_eligible()
        communication_count = Communication.objects.count()
        permission = Permission.objects.get(permission_code="monitoring.reminder.create")
        grant = RolePermission.objects.get(
            role=self.actor.primary_role,
            permission=permission,
        )
        grant.delete()
        denied = self._run_quarter("2026-06-30")
        self.assertEqual(denied.status_code, 403, denied.content)
        grant = RolePermission.objects.create(
            role=self.actor.primary_role,
            permission=permission,
        )

        self.account.member.mobile_number = ""
        self.account.member.save(update_fields=["mobile_number"])
        missing_contact = self._run_quarter("2026-06-30")
        self.assertEqual(missing_contact.status_code, 400, missing_contact.content)

        self.account.member.mobile_number = "+919876543210"
        self.account.member.save(update_fields=["mobile_number"])
        self.sms_template.approval_status = "draft"
        self.sms_template.save(update_fields=["approval_status"])
        unapproved = self._run_quarter("2026-06-30")
        self.assertEqual(unapproved.status_code, 400, unapproved.content)
        self.assertIn(
            "content_template_id", unapproved.json()["error"]["field_errors"]
        )
        self.assertEqual(Reminder.objects.count(), 0)
        self.assertEqual(Communication.objects.count(), communication_count)
        grant.delete()

    def test_out_of_scope_loan_is_not_disclosed_by_manual_reminder_endpoint(self):
        from sfpcl_credit.identity.models import Permission, Role, RolePermission
        from sfpcl_credit.monitoring.models import Reminder

        self._make_eligible()
        scoped_role, _ = Role.objects.get_or_create(
            role_code="senior_manager_finance",
            defaults={"role_name": "Senior Manager Finance", "status": "active"},
        )
        for code in ("finance.loan_account.read", "monitoring.reminder.create"):
            RolePermission.objects.get_or_create(
                role=scoped_role,
                permission=Permission.objects.get(permission_code=code),
            )
        self.actor.primary_role = scoped_role
        self.actor.save(update_fields=["primary_role"])

        response = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/reminders/",
            data=json.dumps(
                {
                    "quarter_end_date": "2026-06-30",
                    "reminder_type": "outstanding_beyond_one_year",
                    "channel": "phone",
                    "message_body": "Quarter-end repayment follow-up call recorded.",
                    "call_outcome": "Borrower will review the repayment schedule.",
                    "contacted_person": "borrower",
                    "next_follow_up_date": "2026-07-07",
                    "send_now": False,
                }
            ),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 404, response.content)
        self.assertNotIn(str(self.account.pk), response.content.decode())
        self.assertEqual(Reminder.objects.count(), 0)

    def _make_eligible(self):
        from sfpcl_credit.loans.models import RepaymentSchedule

        RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=date(2025, 6, 29),
            principal_due="1000.00",
            interest_due="100.00",
            charges_due="0.00",
            total_due="1100.00",
            schedule_status="pending",
        )
        response = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2026-06-30"}),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(response.status_code, 200, response.content)

    def _run_quarter(self, quarter_end_date):
        return self.client.post(
            "/api/v1/reminders/quarter-end-runs/",
            data=json.dumps(
                {
                    "quarter_end_date": quarter_end_date,
                    "channel": "sms",
                    "content_template_id": str(self.sms_template.pk),
                }
            ),
            content_type="application/json",
            **self.auth,
        )
