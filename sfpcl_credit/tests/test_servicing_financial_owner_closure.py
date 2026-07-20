from concurrent.futures import ThreadPoolExecutor
from datetime import date
import tempfile
from threading import Barrier
from unittest import skipUnless
from unittest.mock import patch
from uuid import uuid4

from django.db import close_old_connections, connection, connections
from django.test import TestCase, TransactionTestCase, override_settings

from sfpcl_credit.configurations.models import (
    InterestRateConfig,
    InterestRateConsumptionSnapshot,
    VersionHistory,
)
from sfpcl_credit.configurations.modules.interest_rate_configuration import (
    InterestRateConflict,
    activate,
    consume_effective_rate,
)
from sfpcl_credit.identity.models import User
from sfpcl_credit.processes.loan_servicing import get_ledger
from sfpcl_credit.tests.servicing_builders import (
    append_servicing_ledger_movements,
    build_servicing_owner_fixture,
)


@override_settings(
    DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-servicing-owner-tests-")
)
class ServicingOwnerBuilderTests(TestCase):
    def test_public_builder_produces_distinct_active_financial_owners(self):
        fixture = build_servicing_owner_fixture(suffix=uuid4().hex[:8])

        self.assertEqual(fixture.account.loan_account_status, "active")
        self.assertNotEqual(fixture.maker.pk, fixture.checker.pk)
        permission_codes = set(
            fixture.checker.primary_role.role_permissions.values_list(
                "permission__permission_code", flat=True
            )
        )
        self.assertTrue(
            {
                "config.interest_rate.manage",
                "communications.communication.send",
            }.issubset(permission_codes)
        )

    def test_mixed_ledger_windows_are_exact_at_one_twenty_one_and_one_hundred_one(self):
        from sfpcl_credit.identity.models import Role, User

        fixture = build_servicing_owner_fixture(suffix=uuid4().hex[:8])
        reader = User.objects.create(
            full_name="Ledger Window Accounts Head",
            email=f"ledger.window.{uuid4().hex[:8]}@sfpcl.example",
            status="active",
            primary_role=Role.objects.get(role_code="accounts_head"),
        )
        type(fixture.account).objects.filter(pk=fixture.account.pk).update(
            loan_account_status="sanctioned",
            disbursed_amount="0.00",
            principal_outstanding="0.00",
            total_outstanding="0.00",
        )
        fixture.account.refresh_from_db()

        for added, expected, page in ((1, 1, 1), (20, 21, 2), (80, 101, 6)):
            append_servicing_ledger_movements(
                fixture=fixture,
                count=added,
                start_index=expected - added,
            )
            with patch(
                "sfpcl_credit.processes.loan_servicing._scoped_account",
                return_value=(fixture.account, None),
            ):
                rows, pagination = get_ledger(
                    actor=reader,
                    loan_account_id=fixture.account.pk,
                    query_params={"page": str(page), "page_size": "20"},
                )
            self.assertEqual(pagination["total_count"], expected)
            self.assertEqual(pagination["total_pages"], page)
            self.assertEqual(len(rows), 1)
            self.assertEqual(
                rows[0]["transaction_type"],
                "repayment" if (expected - 1) % 2 == 0 else "reversal",
            )


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
@override_settings(
    DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-servicing-owner-pg-tests-")
)
class ServicingFinancialOwnerPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.fixture = build_servicing_owner_fixture(suffix=uuid4().hex[:8])

    def test_concurrent_exact_consumers_retain_one_snapshot(self):
        rate = self._activate_open_rate("CONSUMER-EXACT")
        consumer_id = uuid4()
        outcomes = self._consumer_race(
            (consumer_id, date(2026, 8, 15)),
            (consumer_id, date(2026, 8, 15)),
        )
        self.assertEqual(outcomes, ["success", "success"])
        self.assertEqual(InterestRateConsumptionSnapshot.objects.count(), 1)
        self.assertEqual(
            InterestRateConsumptionSnapshot.objects.get().rate_config_id, rate.pk
        )

    def test_concurrent_changed_consumers_raise_domain_conflict(self):
        self._activate_open_rate("CONSUMER-CHANGED")
        consumer_id = uuid4()
        outcomes = self._consumer_race(
            (consumer_id, date(2026, 8, 15)),
            (consumer_id, date(2026, 8, 16)),
        )
        self.assertEqual(sorted(outcomes), ["conflict", "success"])
        self.assertEqual(InterestRateConsumptionSnapshot.objects.count(), 1)

    def test_concurrent_competing_successors_retain_one_contiguous_winner(self):
        self._activate_open_rate("PREDECESSOR")
        first = self._proposal("SUCCESSOR-A", date(2026, 9, 1))
        second = self._proposal("SUCCESSOR-B", date(2026, 9, 1))
        outcomes = self._activation_race(
            (first.pk, "successor-a"),
            (second.pk, "successor-b"),
        )
        self.assertEqual(sorted(outcomes), ["conflict", "success"])
        self.assertEqual(InterestRateConfig.objects.filter(status="active").count(), 2)

    def test_concurrent_exact_activation_replay_freezes_one_decision(self):
        row = self._proposal("ACTIVATION-EXACT", date(2026, 8, 1))
        outcomes = self._activation_race(
            (row.pk, "activation-exact"),
            (row.pk, "activation-exact"),
        )
        self.assertEqual(outcomes, ["success", "success"])
        self.assertEqual(
            VersionHistory.objects.filter(
                versioned_entity_type="interest_rate_config",
                versioned_entity_id=row.pk,
            ).count(),
            1,
        )

    def test_concurrent_changed_activation_keys_retain_one_winner(self):
        row = self._proposal("ACTIVATION-CHANGED", date(2026, 8, 1))
        outcomes = self._activation_race(
            (row.pk, "activation-a"),
            (row.pk, "activation-b"),
        )
        self.assertEqual(sorted(outcomes), ["conflict", "success"])
        self.assertEqual(InterestRateConfig.objects.filter(status="active").count(), 1)

    def _activate_open_rate(self, version):
        row = self._proposal(version, date(2026, 8, 1))
        activate(
            actor=self.fixture.checker,
            request=self.fixture.request,
            interest_rate_config_id=row.pk,
            idempotency_key=f"activate-{version.lower()}",
        )
        return row

    def _proposal(self, version, effective_from):
        return InterestRateConfig.objects.create(
            version_number=version,
            rate_type="floating",
            effective_rate="9.2500",
            effective_from=effective_from,
            communication_required=False,
            board_approval_reference=f"BOARD-{version}",
            created_by_user=self.fixture.maker,
        )

    def _consumer_race(self, *items):
        barrier = Barrier(len(items))
        account_id = self.fixture.account.pk

        def contender(item):
            close_old_connections()
            try:
                barrier.wait(timeout=15)
                try:
                    consume_effective_rate(
                        consumer_kind="interest_invoice",
                        consumer_reference_id=item[0],
                        loan_account_id=account_id,
                        calculation_date=item[1],
                    )
                    return "success"
                except InterestRateConflict:
                    return "conflict"
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=len(items)) as pool:
            return list(pool.map(contender, items))

    def _activation_race(self, *items):
        barrier = Barrier(len(items))
        checker_id = self.fixture.checker.pk

        def contender(item):
            close_old_connections()
            try:
                checker = User.objects.get(pk=checker_id)
                barrier.wait(timeout=15)
                try:
                    activate(
                        actor=checker,
                        request=self.fixture.request,
                        interest_rate_config_id=item[0],
                        idempotency_key=item[1],
                    )
                    return "success"
                except InterestRateConflict:
                    return "conflict"
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=len(items)) as pool:
            return list(pool.map(contender, items))
