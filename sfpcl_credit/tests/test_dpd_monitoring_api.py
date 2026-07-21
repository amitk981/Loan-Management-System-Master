import json
from datetime import date
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext


class DpdMonitoringApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.identity.models import Permission, RolePermission
        from sfpcl_credit.tests.test_loan_schedule_ledger_api import (
            LoanScheduleLedgerApiTests,
        )

        fixture = LoanScheduleLedgerApiTests(
            "test_authorised_reader_gets_ordered_decimal_schedule_truth"
        )
        fixture.setUp()
        self.fixture = fixture
        self.account = fixture.account
        self.actor = fixture.fixture.reader
        self.client = Client()
        self.auth = fixture.auth
        for code in ("monitoring.dpd.read", "monitoring.dpd.calculate"):
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

    def test_calculate_first_overdue_day_from_schedule_truth(self):
        from sfpcl_credit.loans.models import RepaymentSchedule

        due_date = date(2026, 6, 30)
        RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=due_date,
            principal_due="1000.00",
            interest_due="100.00",
            charges_due="0.00",
            total_due="1100.00",
            schedule_status="pending",
        )

        response = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2026-07-01"}),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["loan_account_id"], str(self.account.pk))
        self.assertEqual(data["as_of_date"], "2026-07-01")
        self.assertEqual(data["days_past_due"], 1)
        self.assertEqual(data["sop_bucket"], "current")
        self.assertIsNone(data["standard_bucket"])
        self.assertEqual(data["principal_overdue_amount"], "1000.00")
        self.assertEqual(data["interest_overdue_amount"], "100.00")
        self.assertEqual(data["total_overdue_amount"], "1100.00")
        from sfpcl_credit.monitoring.models import DpdStatus

        row = DpdStatus.objects.get()
        self.account.refresh_from_db()
        self.assertEqual(self.account.current_dpd_status_id, row.pk)
        self.assertEqual(row.calculated_by_user_id, self.actor.pk)
        self.assertEqual(row.calculation_audit.action, "monitoring.dpd.calculated")
        self.assertEqual(
            row.calculation_inputs_json["schedule_lines"],
            [
                {
                    "repayment_schedule_id": str(
                        row.loan_account.repayment_schedule_lines.get().pk
                    ),
                    "due_date": "2026-06-30",
                    "principal_due": "1000.00",
                    "interest_due": "100.00",
                    "principal_paid_as_of": "0.00",
                    "interest_paid_as_of": "0.00",
                }
            ],
        )

    def test_read_and_calculate_use_separate_exact_permissions(self):
        from sfpcl_credit.identity.models import Permission, RolePermission

        calculated = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2026-07-01"}),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(calculated.status_code, 200, calculated.content)

        calculate_permission = Permission.objects.get(
            permission_code="monitoring.dpd.calculate"
        )
        RolePermission.objects.filter(
            role=self.actor.primary_role, permission=calculate_permission
        ).delete()
        readable = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/dpd-status/", **self.auth
        )
        denied_write = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2026-07-02"}),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(readable.status_code, 200, readable.content)
        self.assertEqual(
            readable.json()["data"]["dpd_status_id"],
            calculated.json()["data"]["dpd_status_id"],
        )
        self.assertEqual(denied_write.status_code, 403, denied_write.content)

        read_permission = Permission.objects.get(permission_code="monitoring.dpd.read")
        RolePermission.objects.filter(
            role=self.actor.primary_role, permission=read_permission
        ).delete()
        denied_read = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/dpd-status/", **self.auth
        )
        self.assertEqual(denied_read.status_code, 403, denied_read.content)

    def test_portfolio_read_returns_backend_bucket_counts_and_scoped_rows(self):
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
        calculated = self._post_calculation("2026-06-30")
        self.assertEqual(calculated.status_code, 200, calculated.content)

        response = self.client.get("/api/v1/dpd-statuses/", **self.auth)

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(
            data["sop_bucket_counts"],
            {
                "current": 0,
                "one_to_two_years": 1,
                "two_to_three_years": 0,
                "more_than_three_years": 0,
            },
        )
        self.assertEqual(data["total_count"], 1)
        self.assertEqual(data["rows"][0]["loan_account_number"], self.account.loan_account_number)
        self.assertEqual(data["rows"][0]["member_display_name"], self.account.member.display_name)
        self.assertEqual(data["rows"][0]["total_overdue_amount"], "1100.00")

        from sfpcl_credit.identity.models import Permission, RolePermission

        permission = Permission.objects.get(permission_code="monitoring.dpd.read")
        RolePermission.objects.filter(role=self.actor.primary_role, permission=permission).delete()
        denied = self.client.get("/api/v1/dpd-statuses/", **self.auth)
        self.assertEqual(denied.status_code, 403, denied.content)

    def test_bounded_active_portfolio_reports_each_outcome(self):
        from django.db import connection

        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.monitoring.models import DpdStatus
        RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=date(2026, 6, 30),
            principal_due="1000.00",
            interest_due="100.00",
            charges_due="0.00",
            total_due="1100.00",
            schedule_status="pending",
        )

        with CaptureQueriesContext(connection) as queries:
            response = self.client.post(
                "/api/v1/dpd-statuses/bulk-calculate/",
                data=json.dumps(
                    {
                        "as_of_date": "2026-07-01",
                        "loan_account_ids": [],
                        "include_all_active_loans": True,
                    }
                ),
                content_type="application/json",
                **self.auth,
            )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["calculated_count"], 1)
        self.assertEqual(data["skipped_count"], 0)
        self.assertEqual(data["failed_count"], 0)
        self.assertEqual(
            [row["loan_account_id"] for row in data["results"]],
            [str(self.account.pk)],
        )
        self.assertTrue(all(row["outcome"] == "calculated" for row in data["results"]))
        self.assertEqual(DpdStatus.objects.count(), 1)
        self.assertLessEqual(len(queries), 20)

        type(self.account).objects.filter(pk=self.account.pk).update(
            loan_account_status="closed"
        )
        mixed = self.client.post(
            "/api/v1/dpd-statuses/bulk-calculate/",
            data=json.dumps(
                {
                    "as_of_date": "2026-07-02",
                    "loan_account_ids": [str(self.account.pk), str(uuid4())],
                    "include_all_active_loans": False,
                }
            ),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(mixed.status_code, 200, mixed.content)
        self.assertEqual(mixed.json()["data"]["calculated_count"], 0)
        self.assertEqual(mixed.json()["data"]["skipped_count"], 1)
        self.assertEqual(mixed.json()["data"]["failed_count"], 1)
        self.assertEqual(
            [row["outcome"] for row in mixed.json()["data"]["results"]],
            ["skipped", "failed"],
        )

        overflow = self.client.post(
            "/api/v1/dpd-statuses/bulk-calculate/",
            data=json.dumps(
                {
                    "as_of_date": "2026-07-02",
                    "loan_account_ids": [str(self.account.pk)] * 101,
                    "include_all_active_loans": False,
                }
            ),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(overflow.status_code, 400, overflow.content)

    def test_replay_preserves_history_and_does_not_regress_current_pointer(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.monitoring.models import DpdStatus
        from sfpcl_credit.workflows.models import WorkflowEvent

        RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=date(2026, 6, 30),
            principal_due="1000.00",
            interest_due="100.00",
            charges_due="0.00",
            total_due="1100.00",
            schedule_status="pending",
        )
        account_status = self.account.loan_account_status
        workflow_count = WorkflowEvent.objects.count()

        older = self._post_calculation("2026-07-01")
        newer = self._post_calculation("2026-07-31")
        replay = self._post_calculation("2026-07-01")

        self.assertEqual(older.status_code, 200, older.content)
        self.assertEqual(newer.status_code, 200, newer.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], older.json()["data"])
        self.assertEqual(DpdStatus.objects.count(), 2)
        self.assertEqual(
            AuditLog.objects.filter(action="monitoring.dpd.calculated").count(), 2
        )
        self.assertEqual(WorkflowEvent.objects.count(), workflow_count)
        self.account.refresh_from_db()
        self.assertEqual(
            str(self.account.current_dpd_status_id), newer.json()["data"]["dpd_status_id"]
        )
        self.assertEqual(self.account.loan_account_status, account_status)

    def test_calendar_and_configured_operational_bucket_boundaries(self):
        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.monitoring.models import DpdOperationalBucketScheme

        DpdOperationalBucketScheme.objects.create(
            version="DPD-STD-1",
            effective_from=date(2024, 1, 1),
        )
        no_unpaid_schedule = self._post_calculation("2024-02-28")
        self.assertEqual(no_unpaid_schedule.status_code, 200, no_unpaid_schedule.content)
        self.assertEqual(no_unpaid_schedule.json()["data"]["days_past_due"], 0)
        self.assertEqual(no_unpaid_schedule.json()["data"]["sop_bucket"], "current")
        self.assertIsNone(no_unpaid_schedule.json()["data"]["standard_bucket"])

        RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=date(2024, 2, 29),
            principal_due="1000.00",
            interest_due="100.00",
            charges_due="0.00",
            total_due="1100.00",
            schedule_status="pending",
        )
        matrix = (
            ("2024-03-30", 30, "current", "0_30"),
            ("2024-03-31", 31, "current", "31_60"),
            ("2024-04-29", 60, "current", "31_60"),
            ("2024-04-30", 61, "current", "61_90"),
            ("2024-05-29", 90, "current", "61_90"),
            ("2024-05-30", 91, "current", "over_90"),
            ("2025-02-27", 364, "current", "over_90"),
            ("2025-02-28", 365, "one_to_two_years", "over_90"),
            ("2026-02-27", 729, "one_to_two_years", "over_90"),
            ("2026-02-28", 730, "two_to_three_years", "over_90"),
            ("2027-02-28", 1095, "two_to_three_years", "over_90"),
            ("2027-03-01", 1096, "more_than_three_years", "over_90"),
        )
        for as_of_date, days, sop_bucket, standard_bucket in matrix:
            with self.subTest(as_of_date=as_of_date):
                response = self._post_calculation(as_of_date)
                self.assertEqual(response.status_code, 200, response.content)
                data = response.json()["data"]
                self.assertEqual(data["days_past_due"], days)
                self.assertEqual(data["sop_bucket"], sop_bucket)
                self.assertEqual(data["standard_bucket"], standard_bucket)
                self.assertEqual(data["operational_scheme_version"], "DPD-STD-1")

    def test_snapshot_is_unique_per_date_and_append_only(self):
        from sfpcl_credit.monitoring.models import DpdStatus

        calculated = self._post_calculation("2026-07-01")
        self.assertEqual(calculated.status_code, 200, calculated.content)
        row = DpdStatus.objects.get()

        with self.assertRaises(IntegrityError), transaction.atomic():
            DpdStatus.objects.create(
                loan_account=self.account,
                as_of_date=row.as_of_date,
                days_past_due=0,
                sop_bucket="current",
                principal_overdue_amount="0.00",
                interest_overdue_amount="0.00",
                total_overdue_amount="0.00",
                calculated_by_user=self.actor,
                calculation_audit=row.calculation_audit,
            )
        with self.assertRaises(ValidationError):
            DpdStatus.objects.filter(pk=row.pk).update(days_past_due=99)
        row.days_past_due = 99
        with self.assertRaises(ValidationError):
            row.save()
        with self.assertRaises(ValidationError):
            row.delete()

    def test_invalid_inputs_and_future_or_ambiguous_policy_do_not_fabricate_dpd(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.monitoring.models import DpdOperationalBucketScheme, DpdStatus

        future_scheme = DpdOperationalBucketScheme.objects.create(
            version="DPD-FUTURE-1",
            effective_from=date(2027, 1, 1),
        )
        before_effective = self._post_calculation("2026-12-31")
        self.assertEqual(before_effective.status_code, 200, before_effective.content)
        self.assertIsNone(before_effective.json()["data"]["standard_bucket"])
        self.assertIsNone(before_effective.json()["data"]["operational_scheme_version"])

        DpdOperationalBucketScheme.objects.create(
            version="DPD-FUTURE-OVERLAP",
            effective_from=future_scheme.effective_from,
        )
        snapshot_count = DpdStatus.objects.count()
        audit_count = AuditLog.objects.filter(action="monitoring.dpd.calculated").count()
        ambiguous = self._post_calculation("2027-01-01")
        caller_bucket = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/dpd-status/calculate/",
            data=json.dumps(
                {"as_of_date": "2027-01-02", "sop_bucket": "more_than_three_years"}
            ),
            content_type="application/json",
            **self.auth,
        )
        invalid_date = self._post_calculation("not-a-date")

        self.assertEqual(ambiguous.status_code, 409, ambiguous.content)
        self.assertEqual(caller_bucket.status_code, 400, caller_bucket.content)
        self.assertEqual(invalid_date.status_code, 400, invalid_date.content)
        self.assertEqual(DpdStatus.objects.count(), snapshot_count)
        self.assertEqual(
            AuditLog.objects.filter(action="monitoring.dpd.calculated").count(), audit_count
        )

    def _post_calculation(self, as_of_date):
        return self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": as_of_date}),
            content_type="application/json",
            **self.auth,
        )


class DpdPaymentTimingApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.identity.models import Permission, RolePermission
        from sfpcl_credit.tests.test_repayment_allocation_api import (
            RepaymentAllocationApiTests,
        )

        fixture = RepaymentAllocationApiTests(
            "test_partial_receipt_reduces_principal_and_appends_immutable_evidence"
        )
        fixture.setUp()
        self.fixture = fixture
        self.account = fixture.account
        self.actor = fixture.actor
        self.client = Client()
        self.auth = fixture.auth
        for code in ("monitoring.dpd.read", "monitoring.dpd.calculate"):
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

    def test_later_posted_repayment_does_not_reduce_earlier_snapshot(self):
        from sfpcl_credit.loans.models import RepaymentSchedule

        RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=date(2026, 12, 1),
            principal_due="100000.00",
            interest_due="0.00",
            charges_due="0.00",
            total_due="100000.00",
            schedule_status="pending",
        )
        captured = self.fixture.fixture._capture(
            self.fixture.fixture._payload(), "dpd-payment-timing"
        )
        allocated = self.fixture._allocate(captured.json()["data"]["repayment_id"])
        self.assertEqual(allocated.status_code, 200, allocated.content)

        before_payment = self._calculate("2026-12-03")
        on_payment = self._calculate("2026-12-04")

        self.assertEqual(before_payment.status_code, 200, before_payment.content)
        self.assertEqual(on_payment.status_code, 200, on_payment.content)
        self.assertEqual(
            before_payment.json()["data"]["principal_overdue_amount"], "100000.00"
        )
        self.assertEqual(before_payment.json()["data"]["days_past_due"], 2)
        self.assertEqual(on_payment.json()["data"]["principal_overdue_amount"], "0.00")
        self.assertEqual(on_payment.json()["data"]["days_past_due"], 0)

    def _calculate(self, as_of_date):
        return self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": as_of_date}),
            content_type="application/json",
            **self.auth,
        )
