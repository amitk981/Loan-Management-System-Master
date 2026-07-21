import importlib
import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.test import Client, TestCase

from sfpcl_credit.tests.servicing_builders import (
    build_servicing_owner_fixture,
    clone_servicing_account,
)


class DpdPointerIntegrityTests(TestCase):
    def test_database_rejects_dangling_current_pointer(self):
        fixture = build_servicing_owner_fixture(suffix="dpd-pointer-dangling")

        with self.assertRaises(IntegrityError), transaction.atomic():
            type(fixture.account).objects.filter(pk=fixture.account.pk).update(
                current_dpd_status_id=uuid4()
            )

    def test_database_rejects_snapshot_owned_by_another_loan(self):
        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.monitoring.models import DpdStatus
        from sfpcl_credit.tests.test_dpd_monitoring_api import DpdMonitoringApiTests

        source = DpdMonitoringApiTests(
            "test_calculate_first_overdue_day_from_schedule_truth"
        )
        source.setUp()
        RepaymentSchedule.objects.create(
            loan_account=source.account,
            installment_number=1,
            due_date=date(2026, 6, 30),
            principal_due="1000.00",
            interest_due="100.00",
            charges_due="0.00",
            total_due="1100.00",
            schedule_status="pending",
        )
        response = Client().post(
            f"/api/v1/loan-accounts/{source.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2026-07-01"}),
            content_type="application/json",
            **source.auth,
        )
        self.assertEqual(response.status_code, 200, response.content)
        snapshot = DpdStatus.objects.get()
        other_account = clone_servicing_account(
            fixture=source,
            suffix="dpd-pointer-other",
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            type(other_account).objects.filter(pk=other_account.pk).update(
                current_dpd_status_id=snapshot.pk
            )


class DpdPolicyReplayTests(TestCase):
    def test_public_replay_returns_frozen_policy_decision_after_live_scheme_edit(self):
        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.monitoring.models import DpdOperationalBucketScheme
        from sfpcl_credit.tests.test_dpd_monitoring_api import DpdMonitoringApiTests

        fixture = DpdMonitoringApiTests(
            "test_calculate_first_overdue_day_from_schedule_truth"
        )
        fixture.setUp()
        scheme = DpdOperationalBucketScheme.objects.create(
            version="DPD-POLICY-1",
            effective_from=date(2026, 1, 1),
        )
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
        calculated = Client().post(
            f"/api/v1/loan-accounts/{fixture.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2026-07-01"}),
            content_type="application/json",
            **fixture.auth,
        )
        self.assertEqual(calculated.status_code, 200, calculated.content)
        frozen = calculated.json()["data"]["policy_decision"]
        self.assertEqual(frozen["sop_policy_version"], "SFPCL-SOP-DPD-1")
        self.assertEqual(frozen["operational_scheme_id"], str(scheme.pk))
        self.assertEqual(frozen["operational_scheme_version"], "DPD-POLICY-1")
        self.assertEqual(
            frozen["operational_boundaries"],
            {"first_upper_days": 30, "second_upper_days": 60, "third_upper_days": 90},
        )

        with self.assertRaises(ValidationError):
            DpdOperationalBucketScheme.objects.filter(pk=scheme.pk).update(
                version="DPD-POLICY-EDITED"
            )
        replayed = Client().get(
            f"/api/v1/loan-accounts/{fixture.account.pk}/dpd-status/",
            **fixture.auth,
        )

        self.assertEqual(replayed.status_code, 200, replayed.content)
        self.assertEqual(replayed.json()["data"]["policy_decision"], frozen)
        self.assertEqual(
            replayed.json()["data"]["operational_scheme_version"],
            "DPD-POLICY-1",
        )

    def test_migration_backfills_frozen_policy_without_recalculating_dpd(self):
        from django.apps import apps

        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.monitoring.models import (
            DpdOperationalBucketScheme,
            DpdStatus,
        )
        from sfpcl_credit.tests.test_dpd_monitoring_api import DpdMonitoringApiTests

        fixture = DpdMonitoringApiTests(
            "test_calculate_first_overdue_day_from_schedule_truth"
        )
        fixture.setUp()
        scheme = DpdOperationalBucketScheme.objects.create(
            version="DPD-LEGACY-1",
            effective_from=date(2026, 1, 1),
        )
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
        calculated = Client().post(
            f"/api/v1/loan-accounts/{fixture.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2026-07-01"}),
            content_type="application/json",
            **fixture.auth,
        )
        self.assertEqual(calculated.status_code, 200, calculated.content)
        snapshot = DpdStatus.objects.get()
        original_dpd = snapshot.days_past_due
        legacy_inputs = dict(snapshot.calculation_inputs_json)
        legacy_inputs.pop("policy_decision")
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE dpd_statuses SET calculation_inputs_json = %s "
                "WHERE dpd_status_id = %s",
                [json.dumps(legacy_inputs), snapshot.pk.hex],
            )

        migration = importlib.import_module(
            "sfpcl_credit.loans.migrations.0009_dpd_pointer_integrity"
        )
        migration.validate_retained_dpd_pointers(
            apps,
            SimpleNamespace(connection=connection),
        )

        snapshot.refresh_from_db()
        self.assertEqual(snapshot.days_past_due, original_dpd)
        frozen = snapshot.calculation_inputs_json["policy_decision"]
        self.assertEqual(frozen["operational_scheme_id"], str(scheme.pk))
        self.assertEqual(frozen["operational_scheme_version"], "DPD-LEGACY-1")
        self.assertEqual(frozen["sop_policy_version"], "SFPCL-SOP-DPD-1")

    def test_effective_but_unapproved_policy_fails_without_snapshot(self):
        from sfpcl_credit.monitoring.models import (
            DpdOperationalBucketScheme,
            DpdStatus,
        )
        from sfpcl_credit.tests.test_dpd_monitoring_api import DpdMonitoringApiTests

        fixture = DpdMonitoringApiTests(
            "test_calculate_first_overdue_day_from_schedule_truth"
        )
        fixture.setUp()
        DpdOperationalBucketScheme.objects.create(
            version="DPD-RETIRED-1",
            effective_from=date(2026, 1, 1),
            status="retired",
        )

        response = Client().post(
            f"/api/v1/loan-accounts/{fixture.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2026-07-01"}),
            content_type="application/json",
            **fixture.auth,
        )

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(DpdStatus.objects.count(), 0)
        fixture.account.refresh_from_db()
        self.assertIsNone(fixture.account.current_dpd_status_id)


class DpdSourceOwnerDecisionTests(TestCase):
    def test_public_owner_decision_freezes_locked_schedule_truth(self):
        from django.db import transaction

        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.loans.modules.dpd_source_decision import (
            resolve_locked_dpd_source_decision,
        )
        from sfpcl_credit.tests.test_dpd_monitoring_api import DpdMonitoringApiTests

        fixture = DpdMonitoringApiTests(
            "test_calculate_first_overdue_day_from_schedule_truth"
        )
        fixture.setUp()
        schedule = RepaymentSchedule.objects.create(
            loan_account=fixture.account,
            installment_number=1,
            due_date=date(2026, 6, 30),
            principal_due="1000.00",
            interest_due="100.00",
            charges_due="0.00",
            total_due="1100.00",
            schedule_status="pending",
        )

        with transaction.atomic():
            decision = resolve_locked_dpd_source_decision(
                actor=fixture.actor,
                loan_account_id=fixture.account.pk,
                as_of_date=date(2026, 7, 1),
            )

        self.assertEqual(decision.loan_account_id, fixture.account.pk)
        self.assertEqual(decision.loan_account_status, "active")
        self.assertEqual(decision.as_of_date, date(2026, 7, 1))
        self.assertEqual(len(decision.schedule_lines), 1)
        self.assertEqual(decision.schedule_lines[0].repayment_schedule_id, schedule.pk)
        self.assertEqual(decision.schedule_lines[0].principal_paid_as_of, 0)
        self.assertEqual(decision.schedule_lines[0].interest_paid_as_of, 0)

    def test_monitoring_consumes_only_the_public_loan_source_decision(self):
        source = (
            Path(__file__).parents[1]
            / "monitoring"
            / "modules"
            / "dpd_monitoring.py"
        ).read_text()

        self.assertIn(
            "from sfpcl_credit.loans.modules.dpd_source_decision import",
            source,
        )
        self.assertNotIn("RepaymentSchedule,", source)
        self.assertNotIn("RepaymentScheduleAllocation,", source)
