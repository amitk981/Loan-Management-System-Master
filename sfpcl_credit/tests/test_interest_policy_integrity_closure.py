from datetime import date
from decimal import Decimal
import tempfile
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from sfpcl_credit.interest.models import InterestInvoiceConfiguration
from sfpcl_credit.interest.modules.as_of_accounting import decide_interest_as_of
from sfpcl_credit.tests.servicing_builders import (
    activate_interest_rate,
    build_approved_interest_calculation_policy,
    build_interest_rate_proposal,
    build_servicing_owner_fixture,
)


@override_settings(
    DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-interest-policy-tests-")
)
class InterestPolicyIntegrityClosureTests(TestCase):
    def setUp(self):
        self.fixture = build_servicing_owner_fixture(suffix=uuid4().hex[:8])

    def test_approved_policy_is_immutable_before_consumption_and_amends_by_version(self):
        approved = self._approved_policy("ROUNDING-V1")

        approved.day_count_basis = 360
        with self.assertRaises(ValidationError):
            approved.save(update_fields=["day_count_basis"])
        with self.assertRaises(ValidationError):
            InterestInvoiceConfiguration.objects.filter(pk=approved.pk).update(
                day_count_basis=360
            )
        with self.assertRaises(ValidationError):
            InterestInvoiceConfiguration.objects.bulk_update(
                [approved], ["day_count_basis"]
            )
        with self.assertRaises(ValidationError):
            approved.delete()
        with self.assertRaises(ValidationError):
            InterestInvoiceConfiguration.objects.filter(pk=approved.pk).delete()

        amendment = self._approved_policy("ROUNDING-V2", start=date(2027, 4, 1))
        self.assertNotEqual(amendment.pk, approved.pk)
        self.assertEqual(
            InterestInvoiceConfiguration.objects.filter(status="active").count(), 2
        )

    def test_approved_policy_rounds_once_after_multi_segment_half_unit_decision(self):
        policy = self._approved_policy("ROUNDING-HALF-UNIT")
        type(self.fixture.account).objects.filter(pk=self.fixture.account.pk).update(
            disbursed_amount="1.00",
            principal_outstanding="1.00",
            total_outstanding="1.00",
        )
        self.fixture.account.refresh_from_db()
        first = build_interest_rate_proposal(
            fixture=self.fixture,
            version="ROUNDING-RATE-A",
            effective_from=date(2026, 4, 1),
            rate="91.2500",
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=first,
            idempotency_key="rounding-rate-a",
        )
        second = build_interest_rate_proposal(
            fixture=self.fixture,
            version="ROUNDING-RATE-B",
            effective_from=date(2026, 4, 2),
            rate="91.2500",
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=second,
            idempotency_key="rounding-rate-b",
        )

        decision = decide_interest_as_of(
            account=self.fixture.account,
            period_start=date(2026, 4, 1),
            period_end=date(2026, 4, 2),
            configuration=policy,
        )

        self.assertEqual(decision.gross_interest_amount, Decimal("0.01"))
        self.assertEqual(
            [segment["gross_interest_amount"] for segment in decision.snapshot()],
            ["0.002500", "0.002500"],
        )

    def test_missing_rounding_policy_fails_before_financial_evidence_write(self):
        from sfpcl_credit.interest.models import AccrualEntry, InterestInvoice

        policy = InterestInvoiceConfiguration.objects.create(
            version_number="ROUNDING-MISSING",
            effective_from=date(2026, 4, 1),
            effective_to=date(2027, 3, 31),
            calculation_method="simple_daily",
            day_count_basis=365,
            tax_rate="0.0000",
            fixed_fee_amount="0.00",
            owner_role_codes=["accounts_head"],
            status="active",
            approved_by_user=self.fixture.maker,
        )
        before = (InterestInvoice.objects.count(), AccrualEntry.objects.count())

        with self.assertRaisesRegex(ValueError, "rounding policy"):
            decide_interest_as_of(
                account=self.fixture.account,
                period_start=date(2026, 4, 1),
                period_end=date(2026, 4, 30),
                configuration=policy,
            )

        self.assertEqual(
            (InterestInvoice.objects.count(), AccrualEntry.objects.count()), before
        )

    def _approved_policy(self, version, *, start=date(2026, 4, 1)):
        return build_approved_interest_calculation_policy(
            fixture=self.fixture,
            version=version,
            effective_from=start,
            effective_to=date(start.year + 1, 3, 31),
        )
