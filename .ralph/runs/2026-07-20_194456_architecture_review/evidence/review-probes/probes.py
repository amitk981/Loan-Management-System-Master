import sys
import unittest
from datetime import date

import django
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.test.runner import DiscoverRunner
from django.utils import timezone


class RateCurrentDateProbe(TestCase):
    def test_future_rate_cannot_be_published_before_its_effective_date(self):
        from sfpcl_credit.configurations.modules.interest_rate_configuration import (
            InterestRateConflict,
            converge_current_rate_projection,
        )
        from sfpcl_credit.tests.servicing_builders import (
            activate_interest_rate,
            build_interest_rate_proposal,
            build_servicing_owner_fixture,
        )

        fixture = build_servicing_owner_fixture(suffix="reviewrate")
        current = build_interest_rate_proposal(
            fixture=fixture, version="REVIEW-CURRENT",
            effective_from=date(2026, 7, 1), rate="9.2500",
        )
        activate_interest_rate(
            fixture=fixture, proposal=current, idempotency_key="review-current"
        )
        successor = build_interest_rate_proposal(
            fixture=fixture, version="REVIEW-FUTURE",
            effective_from=date(2026, 9, 1), rate="9.7500",
        )
        activate_interest_rate(
            fixture=fixture, proposal=successor, idempotency_key="review-future"
        )
        self.assertLess(timezone.localdate(), successor.effective_from)
        with self.assertRaises(InterestRateConflict):
            converge_current_rate_projection(
                actor=fixture.checker,
                request=fixture.request,
                loan_account_id=fixture.account.pk,
                as_of_date=successor.effective_from,
            )
        fixture.account.refresh_from_db()
        self.assertEqual(fixture.account.current_interest_rate, current.effective_rate)


class InterestConfigurationProbe(TestCase):
    def test_approved_configuration_is_immutable_before_first_consumption(self):
        from sfpcl_credit.identity.models import Role, User
        from sfpcl_credit.interest.models import InterestInvoiceConfiguration

        role, _ = Role.objects.get_or_create(
            role_code="accounts_head",
            defaults={"role_name": "Accounts Head", "status": "active"},
        )
        approver = User.objects.create(
            full_name="Review Interest Approver",
            email="review.interest.approver@example.test",
            status="active",
            primary_role=role,
        )
        config = InterestInvoiceConfiguration.objects.create(
            version_number="REVIEW-CONFIG-1",
            effective_from=date(2026, 4, 1),
            effective_to=date(2027, 3, 31),
            calculation_method="simple_daily",
            day_count_basis=365,
            tax_rate="0.0000",
            fixed_fee_amount="0.00",
            owner_role_codes=["accounts_head"],
            status="active",
            approved_by_user=approver,
        )
        config.day_count_basis = 360
        with self.assertRaises(ValidationError):
            config.save(update_fields=["day_count_basis"])


class DpdPointerProbe(TestCase):
    def test_current_dpd_pointer_has_database_referential_integrity(self):
        from uuid import uuid4

        from django.db import IntegrityError, transaction
        from sfpcl_credit.tests.servicing_builders import build_servicing_owner_fixture

        fixture = build_servicing_owner_fixture(suffix="reviewdpd")
        with self.assertRaises(IntegrityError), transaction.atomic():
            type(fixture.account).objects.filter(pk=fixture.account.pk).update(
                current_dpd_status_id=uuid4()
            )


class ReminderChangedKeyProbe(TestCase):
    def test_changed_send_key_returns_conflict_instead_of_server_error(self):
        from sfpcl_credit.tests.test_reminder_queue_api import ReminderQueueApiTests

        fixture = ReminderQueueApiTests(
            "test_electronic_send_uses_worker_and_projects_provider_accepted_truth"
        )
        fixture.setUp()
        fixture._make_eligible()
        created = fixture.client.post(
            f"/api/v1/loan-accounts/{fixture.account.pk}/reminders/",
            data=__import__("json").dumps(
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
        first = fixture.client.post(
            f"/api/v1/reminders/{reminder_id}/send/",
            data="{}", content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="review-send-first", **fixture.auth,
        )
        self.assertEqual(first.status_code, 200, first.content)
        changed = fixture.client.post(
            f"/api/v1/reminders/{reminder_id}/send/",
            data="{}", content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="review-send-changed", **fixture.auth,
        )
        self.assertEqual(changed.status_code, 409, changed.content)


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
