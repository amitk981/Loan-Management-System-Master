from concurrent.futures import ThreadPoolExecutor
from datetime import date
import tempfile
from threading import Barrier
from unittest import skipUnless
from unittest.mock import patch
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import (
    IntegrityError,
    close_old_connections,
    connection,
    connections,
    transaction,
)
from django.utils import timezone
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
    resolve_effective_rate,
)
from sfpcl_credit.identity.models import AuditLog, User
from sfpcl_credit.processes.loan_servicing import get_ledger
from sfpcl_credit.tests.servicing_builders import (
    activate_interest_rate,
    append_servicing_ledger_movements,
    build_interest_rate_proposal,
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


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
@override_settings(
    DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-rate-effective-date-pg-tests-")
)
class RateEffectiveDatePostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.fixture = build_servicing_owner_fixture(suffix=uuid4().hex[:8])

    def test_active_rate_write_paths_require_the_canonical_approval_decision(self):
        fabricated = InterestRateConfig(
            version_number="FABRICATED-ACTIVE",
            rate_type="floating",
            effective_rate="9.7500",
            effective_from=date(2026, 9, 1),
            communication_required=False,
            board_approval_reference="BOARD-FABRICATED",
            status=InterestRateConfig.STATUS_ACTIVE,
            created_by_user=self.fixture.maker,
            approved_by_user=self.fixture.checker,
            activated_at=timezone.now(),
            activation_idempotency_key="fabricated-active",
            activation_payload_digest="a" * 64,
        )

        with self.assertRaises(ValidationError):
            InterestRateConfig.objects.bulk_create([fabricated])

        self.assertFalse(
            InterestRateConfig.objects.filter(version_number="FABRICATED-ACTIVE").exists()
        )
        approved = build_interest_rate_proposal(
            fixture=self.fixture,
            version="CANONICAL-ACTIVE",
            effective_from=date(2026, 7, 1),
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=approved,
            idempotency_key="canonical-active",
        )
        approved.refresh_from_db()
        approved.effective_rate = "10.0000"
        with self.assertRaises(ValidationError):
            approved.save(update_fields=["effective_rate"])
        with self.assertRaises(ValidationError):
            InterestRateConfig.objects.filter(pk=approved.pk).update(
                effective_rate="10.0000"
            )
        with self.assertRaises(ValidationError):
            InterestRateConfig.objects.bulk_update([approved], ["effective_rate"])
        with self.assertRaises(ValidationError):
            approved.delete()
        with self.assertRaises(ValidationError):
            InterestRateConfig.objects.filter(pk=approved.pk).delete()

        incoherent = build_interest_rate_proposal(
            fixture=self.fixture,
            version="DATABASE-INCOHERENT",
            effective_from=date(2026, 9, 1),
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE interest_rate_configs SET status = %s WHERE interest_rate_config_id = %s",
                    [InterestRateConfig.STATUS_ACTIVE, incoherent.pk.hex],
                )

    def test_future_activation_waits_for_its_effective_date_in_the_loan_projection(self):
        current = build_interest_rate_proposal(
            fixture=self.fixture,
            version="CURRENT-RATE",
            effective_from=date(2026, 7, 1),
            rate="9.2500",
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=current,
            idempotency_key="activate-current-rate",
        )
        successor = build_interest_rate_proposal(
            fixture=self.fixture,
            version="FUTURE-RATE",
            effective_from=date(2026, 9, 1),
            rate="9.7500",
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=successor,
            idempotency_key="activate-future-rate",
        )

        self.fixture.account.refresh_from_db()
        self.assertEqual(
            f"{self.fixture.account.current_interest_rate:.4f}",
            f"{current.effective_rate}",
        )
        self.assertEqual(
            resolve_effective_rate(date(2026, 8, 31)).interest_rate_config_id,
            current.pk,
        )
        self.assertEqual(
            resolve_effective_rate(date(2026, 9, 1)).interest_rate_config_id,
            successor.pk,
        )

    def test_due_date_projection_convergence_is_public_idempotent_and_audited(self):
        from sfpcl_credit.configurations.modules.interest_rate_configuration import (
            converge_current_rate_projection,
        )

        current = build_interest_rate_proposal(
            fixture=self.fixture,
            version="CONVERGE-CURRENT",
            effective_from=date(2026, 7, 1),
            rate="9.2500",
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=current,
            idempotency_key="converge-current",
        )
        successor = build_interest_rate_proposal(
            fixture=self.fixture,
            version="CONVERGE-FUTURE",
            effective_from=date(2026, 9, 1),
            rate="9.7500",
        )
        activated = activate_interest_rate(
            fixture=self.fixture,
            proposal=successor,
            idempotency_key="converge-future",
        )

        projection = converge_current_rate_projection(
            actor=self.fixture.checker,
            request=self.fixture.request,
            loan_account_id=self.fixture.account.pk,
            as_of_date=date(2026, 9, 1),
        )
        replayed_projection = converge_current_rate_projection(
            actor=self.fixture.checker,
            request=self.fixture.request,
            loan_account_id=self.fixture.account.pk,
            as_of_date=date(2026, 9, 1),
        )
        activation_replay = activate_interest_rate(
            fixture=self.fixture,
            proposal=successor,
            idempotency_key="converge-future",
        )

        self.assertTrue(projection.projection_changed)
        self.assertFalse(replayed_projection.projection_changed)
        self.fixture.account.refresh_from_db()
        self.assertEqual(
            f"{self.fixture.account.current_interest_rate:.4f}",
            f"{successor.effective_rate}",
        )
        self.assertEqual(activation_replay["original_response"], activated)
        self.assertEqual(
            AuditLog.objects.filter(
                action="config.interest_rate.loan_projection_converged",
                entity_id=self.fixture.account.pk,
            ).count(),
            1,
        )

    def test_consumed_boundary_and_competing_successors_retain_one_decision(self):
        from sfpcl_credit.tests.servicing_builders import (
            race_interest_rate_activations,
        )

        predecessor = build_interest_rate_proposal(
            fixture=self.fixture,
            version="BOUNDARY-PREDECESSOR",
            effective_from=date(2026, 7, 1),
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=predecessor,
            idempotency_key="boundary-predecessor",
        )
        consume_effective_rate(
            consumer_kind="interest_invoice",
            consumer_reference_id=uuid4(),
            loan_account_id=self.fixture.account.pk,
            calculation_date=date(2026, 8, 31),
        )
        invalid = build_interest_rate_proposal(
            fixture=self.fixture,
            version="CONSUMED-BACKDATE",
            effective_from=date(2026, 8, 15),
        )
        with self.assertRaises(InterestRateConflict):
            activate_interest_rate(
                fixture=self.fixture,
                proposal=invalid,
                idempotency_key="consumed-backdate",
            )

        proposals = [
            build_interest_rate_proposal(
                fixture=self.fixture,
                version=f"BOUNDARY-SUCCESSOR-{suffix}",
                effective_from=date(2026, 9, 1),
                rate="9.7500",
            )
            for suffix in ("A", "B")
        ]
        keys = ["boundary-successor-a", "boundary-successor-b"]
        outcomes = race_interest_rate_activations(
            fixture=self.fixture,
            proposals=proposals,
            idempotency_keys=keys,
        )
        winner_index = outcomes.index("success")
        winner = proposals[winner_index]
        winner_key = keys[winner_index]

        self.assertEqual(sorted(outcomes), ["conflict", "success"])
        predecessor.refresh_from_db()
        self.assertEqual(predecessor.effective_to, date(2026, 8, 31))
        replay = activate_interest_rate(
            fixture=self.fixture,
            proposal=winner,
            idempotency_key=winner_key,
        )
        self.assertTrue(replay["idempotency_replayed"])
        with self.assertRaises(InterestRateConflict):
            activate_interest_rate(
                fixture=self.fixture,
                proposal=winner,
                idempotency_key="changed-winner-key",
            )
        self.assertEqual(
            VersionHistory.objects.filter(
                versioned_entity_type="interest_rate_config",
                versioned_entity_id=winner.pk,
            ).count(),
            1,
        )
