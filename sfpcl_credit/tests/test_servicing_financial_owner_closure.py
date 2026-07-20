from concurrent.futures import ThreadPoolExecutor
from datetime import date
import tempfile
from threading import Barrier
from types import SimpleNamespace
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
from sfpcl_credit.identity.models import AuditLog, Permission, Role, RolePermission, User
from sfpcl_credit.identity.modules import auth_service
from sfpcl_credit.processes.loan_servicing import get_ledger
from sfpcl_credit.tests.servicing_builders import (
    activate_interest_rate,
    append_servicing_ledger_movements,
    build_interest_rate_proposal,
    build_servicing_owner_fixture,
    clone_servicing_account,
    restore_servicing_account_to_created_read_state,
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


@override_settings(
    DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-rate-current-date-tests-")
)
class RateCurrentDateFinalizerTests(TestCase):
    def setUp(self):
        self.fixture = build_servicing_owner_fixture(suffix=uuid4().hex[:8])
        self.reader = User.objects.create(
            full_name="Rate Finalizer Portfolio Reader",
            email=f"rate.finalizer.reader.{uuid4().hex[:8]}@sfpcl.example",
            status="active",
            primary_role=Role.objects.get(role_code="accounts_head"),
        )

    def test_public_owner_cannot_publish_future_rate_before_server_date(self):
        from sfpcl_credit.configurations.modules.interest_rate_configuration import (
            publish_current_rate_projection,
        )

        current = build_interest_rate_proposal(
            fixture=self.fixture,
            version="FINALIZER-EARLY-CURRENT",
            effective_from=date(2026, 7, 1),
            rate="9.2500",
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=current,
            idempotency_key="finalizer-early-current",
        )
        successor = build_interest_rate_proposal(
            fixture=self.fixture,
            version="FINALIZER-EARLY-FUTURE",
            effective_from=date(2026, 9, 1),
            rate="9.7500",
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=successor,
            idempotency_key="finalizer-early-future",
        )

        with patch(
            "sfpcl_credit.configurations.modules.interest_rate_configuration.timezone.localdate",
            return_value=date(2026, 7, 20),
        ):
            projection = publish_current_rate_projection(
                actor=self.fixture.maker,
                request=self.fixture.request,
                loan_account_id=self.fixture.account.pk,
                idempotency_key="finalizer-owner:2026-07-20",
            )

        self.fixture.account.refresh_from_db()
        self.assertFalse(projection.projection_changed)
        self.assertEqual(projection.as_of_date, date(2026, 7, 20))
        self.assertEqual(f"{self.fixture.account.current_interest_rate:.4f}", "9.2500")

    def test_public_owner_retains_one_immutable_idempotency_decision(self):
        from sfpcl_credit.configurations.models import CurrentRateProjectionDecision
        from sfpcl_credit.configurations.modules.interest_rate_configuration import (
            publish_current_rate_projection,
        )

        current = build_interest_rate_proposal(
            fixture=self.fixture,
            version="FINALIZER-REPLAY-CURRENT",
            effective_from=date(2026, 7, 1),
            rate="9.2500",
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=current,
            idempotency_key="finalizer-replay-current",
        )
        successor = build_interest_rate_proposal(
            fixture=self.fixture,
            version="FINALIZER-REPLAY-DUE",
            effective_from=date(2026, 9, 1),
            rate="9.7500",
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=successor,
            idempotency_key="finalizer-replay-due",
        )
        with patch(
            "sfpcl_credit.configurations.modules.interest_rate_configuration.timezone.localdate",
            return_value=date(2026, 9, 1),
        ):
            first = publish_current_rate_projection(
                actor=self.fixture.maker,
                request=self.fixture.request,
                loan_account_id=self.fixture.account.pk,
                idempotency_key="finalizer-projection-decision",
            )
            replay = publish_current_rate_projection(
                actor=self.fixture.maker,
                request=self.fixture.request,
                loan_account_id=self.fixture.account.pk,
                idempotency_key="finalizer-projection-decision",
            )
            with self.assertRaises(InterestRateConflict):
                publish_current_rate_projection(
                    actor=self.fixture.maker,
                    request=self.fixture.request,
                    loan_account_id=self.fixture.account.pk,
                    idempotency_key="finalizer-projection-changed",
                )
            self.assertEqual(CurrentRateProjectionDecision.objects.count(), 1)

        self.assertTrue(first.projection_changed)
        self.assertTrue(replay.idempotency_replayed)
        self.assertEqual(CurrentRateProjectionDecision.objects.count(), 1)
        decision = CurrentRateProjectionDecision.objects.get()
        self.assertIn("config.interest_rate.manage", set(
            auth_service.effective_permission_codes(decision.actor_user)
        ))
        self.assertTrue(decision.actor_role_codes_json)
        decision.projection_changed = False
        with self.assertRaises(ValidationError):
            decision.save(update_fields=["projection_changed"])
        with self.assertRaises(ValidationError):
            CurrentRateProjectionDecision.objects.filter(pk=decision.pk).update(
                projection_changed=False
            )
        with self.assertRaises(ValidationError):
            CurrentRateProjectionDecision.objects.filter(pk=decision.pk).delete()
        with self.assertRaises(ValidationError):
            CurrentRateProjectionDecision.objects.bulk_create([decision])
        self.assertEqual(
            AuditLog.objects.filter(
                action="config.interest_rate.loan_projection_converged",
                entity_id=self.fixture.account.pk,
            ).count(),
            1,
        )

    def test_due_owner_keeps_stale_account_in_collection_and_detail(self):
        from sfpcl_credit.processes.loan_account_360 import get_account, list_accounts

        current = build_interest_rate_proposal(
            fixture=self.fixture,
            version="FINALIZER-VISIBLE-CURRENT",
            effective_from=date(2026, 7, 1),
            rate="9.2500",
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=current,
            idempotency_key="finalizer-visible-current",
        )
        successor = build_interest_rate_proposal(
            fixture=self.fixture,
            version="FINALIZER-VISIBLE-DUE",
            effective_from=date(2026, 9, 1),
            rate="9.7500",
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=successor,
            idempotency_key="finalizer-visible-due",
        )
        restore_servicing_account_to_created_read_state(fixture=self.fixture)

        with patch(
            "sfpcl_credit.configurations.modules.interest_rate_configuration.timezone.localdate",
            return_value=date(2026, 9, 1),
        ):
            rows, pagination = list_accounts(actor=self.reader, query_params={})
            self.assertEqual(pagination["total_count"], 1)
            self.assertEqual(
                [row["loan_account_id"] for row in rows],
                [str(self.fixture.account.pk)],
            )
            detail = get_account(
                actor=self.reader,
                loan_account_id=self.fixture.account.pk,
            )

        self.fixture.account.refresh_from_db()
        self.assertEqual(rows[0]["current_interest_rate"], "9.7500")
        self.assertEqual(detail["current_interest_rate"], "9.7500")
        self.assertEqual(f"{self.fixture.account.current_interest_rate:.4f}", "9.7500")

    def test_system_owner_repairs_a_stale_scalar_from_its_retained_decision(self):
        from sfpcl_credit.configurations.models import CurrentRateProjectionDecision
        from sfpcl_credit.configurations.modules.interest_rate_configuration import (
            publish_current_rate_projection,
            run_due_current_rate_projections,
        )

        current = build_interest_rate_proposal(
            fixture=self.fixture,
            version="FINALIZER-REPAIR-CURRENT",
            effective_from=date(2026, 7, 1),
            rate="9.2500",
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=current,
            idempotency_key="finalizer-repair-current",
        )
        successor = build_interest_rate_proposal(
            fixture=self.fixture,
            version="FINALIZER-REPAIR-DUE",
            effective_from=date(2026, 9, 1),
            rate="9.7500",
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=successor,
            idempotency_key="finalizer-repair-due",
        )
        with patch(
            "sfpcl_credit.configurations.modules.interest_rate_configuration.timezone.localdate",
            return_value=date(2026, 9, 1),
        ):
            publish_current_rate_projection(
                actor=self.fixture.maker,
                request=self.fixture.request,
                loan_account_id=self.fixture.account.pk,
                idempotency_key="finalizer-repair-manual-decision",
            )
            type(self.fixture.account).objects.filter(pk=self.fixture.account.pk).update(
                current_interest_rate="9.2500"
            )
            repaired = run_due_current_rate_projections(
                loan_account_ids=[self.fixture.account.pk], limit=1
            )

        self.fixture.account.refresh_from_db()
        self.assertEqual(len(repaired), 1)
        self.assertEqual(f"{self.fixture.account.current_interest_rate:.4f}", "9.7500")
        self.assertEqual(CurrentRateProjectionDecision.objects.count(), 1)
        repair_audit = AuditLog.objects.get(
            action="config.interest_rate.loan_projection_repaired"
        )
        self.assertIsNone(repair_audit.actor_user_id)
        self.assertEqual(repair_audit.actor_type, "system")

    def test_bounded_system_owner_processes_distinct_accounts(self):
        from sfpcl_credit.configurations.models import CurrentRateProjectionDecision
        from sfpcl_credit.configurations.modules.interest_rate_configuration import (
            run_due_current_rate_projections,
        )

        other_account = clone_servicing_account(
            fixture=self.fixture, suffix=uuid4().hex[:8]
        )
        current = build_interest_rate_proposal(
            fixture=self.fixture,
            version="FINALIZER-BOUNDED-CURRENT",
            effective_from=date(2026, 7, 1),
            rate="9.2500",
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=current,
            idempotency_key="finalizer-bounded-current",
        )
        successor = build_interest_rate_proposal(
            fixture=self.fixture,
            version="FINALIZER-BOUNDED-DUE",
            effective_from=date(2026, 9, 1),
            rate="9.7500",
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=successor,
            idempotency_key="finalizer-bounded-due",
        )
        with patch(
            "sfpcl_credit.configurations.modules.interest_rate_configuration.timezone.localdate",
            return_value=date(2026, 9, 1),
        ):
            first = run_due_current_rate_projections(limit=1)
            second = run_due_current_rate_projections(limit=1)
            exhausted = run_due_current_rate_projections(limit=1)

        self.assertEqual([len(first), len(second), len(exhausted)], [1, 1, 0])
        self.assertEqual(CurrentRateProjectionDecision.objects.count(), 2)
        for account in (self.fixture.account, other_account):
            account.refresh_from_db()
            self.assertEqual(f"{account.current_interest_rate:.4f}", "9.7500")

    def test_manual_owner_rejects_missing_permission_and_account_scope(self):
        from sfpcl_credit.configurations.models import CurrentRateProjectionDecision
        from sfpcl_credit.configurations.modules.interest_rate_configuration import (
            publish_current_rate_projection,
        )

        current = build_interest_rate_proposal(
            fixture=self.fixture,
            version="FINALIZER-SCOPE-CURRENT",
            effective_from=date(2026, 7, 1),
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=current,
            idempotency_key="finalizer-scope-current",
        )
        with self.assertRaises(InterestRateConflict):
            publish_current_rate_projection(
                actor=self.reader,
                request=None,
                loan_account_id=self.fixture.account.pk,
                idempotency_key="finalizer-missing-permission",
            )
        with self.assertRaises(InterestRateConflict):
            publish_current_rate_projection(
                actor=self.fixture.checker,
                request=None,
                loan_account_id=self.fixture.account.pk,
                idempotency_key="finalizer-out-of-scope",
            )
        self.assertEqual(CurrentRateProjectionDecision.objects.count(), 0)

    def test_runtime_task_delegates_to_bounded_current_date_owner(self):
        from sfpcl_credit.config.celery import app
        from sfpcl_credit.processes.tasks import dispatch_due_current_rate_projections

        app.loader.import_default_modules()
        projection = SimpleNamespace(loan_account_id=self.fixture.account.pk)
        with patch(
            "sfpcl_credit.processes.tasks.run_due_current_rate_projections",
            return_value=[projection],
        ) as owner:
            result = dispatch_due_current_rate_projections()

        self.assertEqual(
            result,
            {
                "processed_count": 1,
                "loan_account_ids": [str(self.fixture.account.pk)],
            },
        )
        owner.assert_called_once_with(limit=100)
        self.assertIn("configurations.publish_due_current_rates", app.tasks)

    def test_before_date_after_matrix_aligns_reads_and_interest_consumers(self):
        from sfpcl_credit.configurations.modules.interest_rate_configuration import (
            run_due_current_rate_projections,
        )
        from sfpcl_credit.processes.loan_account_360 import get_account, list_accounts

        current = build_interest_rate_proposal(
            fixture=self.fixture,
            version="FINALIZER-MATRIX-CURRENT",
            effective_from=date(2026, 7, 1),
            rate="9.2500",
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=current,
            idempotency_key="finalizer-matrix-current",
        )
        successor = build_interest_rate_proposal(
            fixture=self.fixture,
            version="FINALIZER-MATRIX-DUE",
            effective_from=date(2026, 9, 1),
            rate="9.7500",
        )
        activate_interest_rate(
            fixture=self.fixture,
            proposal=successor,
            idempotency_key="finalizer-matrix-due",
        )
        restore_servicing_account_to_created_read_state(fixture=self.fixture)

        for boundary_date, expected_version, expected_rate in (
            (date(2026, 8, 31), current.version_number, "9.2500"),
            (date(2026, 9, 1), successor.version_number, "9.7500"),
            (date(2026, 9, 2), successor.version_number, "9.7500"),
        ):
            with self.subTest(boundary_date=boundary_date), patch(
                "sfpcl_credit.configurations.modules.interest_rate_configuration.timezone.localdate",
                return_value=boundary_date,
            ):
                run_due_current_rate_projections(
                    loan_account_ids=[self.fixture.account.pk],
                    limit=1,
                )
                rows, pagination = list_accounts(
                    actor=self.reader,
                    query_params={},
                )
                detail = get_account(
                    actor=self.reader,
                    loan_account_id=self.fixture.account.pk,
                )
                resolved = resolve_effective_rate(boundary_date)
                invoice_rate = consume_effective_rate(
                    consumer_kind="interest_invoice",
                    consumer_reference_id=uuid4(),
                    loan_account_id=self.fixture.account.pk,
                    calculation_date=boundary_date,
                )
                accrual_rate = consume_effective_rate(
                    consumer_kind="interest_accrual",
                    consumer_reference_id=uuid4(),
                    loan_account_id=self.fixture.account.pk,
                    calculation_date=boundary_date,
                )

            self.fixture.account.refresh_from_db()
            self.assertEqual(pagination["total_count"], 1)
            self.assertEqual(rows[0]["current_interest_rate"], expected_rate)
            self.assertEqual(detail["current_interest_rate"], expected_rate)
            self.assertEqual(f"{self.fixture.account.current_interest_rate:.4f}", expected_rate)
            self.assertEqual(resolved.version_number, expected_version)
            self.assertEqual(invoice_rate.version_number, expected_version)
            self.assertEqual(accrual_rate.version_number, expected_version)


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
            publish_current_rate_projection,
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

        with patch(
            "sfpcl_credit.configurations.modules.interest_rate_configuration.timezone.localdate",
            return_value=date(2026, 9, 1),
        ):
            projection = publish_current_rate_projection(
                actor=self.fixture.maker,
                request=self.fixture.request,
                loan_account_id=self.fixture.account.pk,
                idempotency_key="effective-date-current-projection",
            )
            replayed_projection = publish_current_rate_projection(
                actor=self.fixture.maker,
                request=self.fixture.request,
                loan_account_id=self.fixture.account.pk,
                idempotency_key="effective-date-current-projection",
            )
        activation_replay = activate_interest_rate(
            fixture=self.fixture,
            proposal=successor,
            idempotency_key="converge-future",
        )

        self.assertTrue(projection.projection_changed)
        self.assertTrue(replayed_projection.idempotency_replayed)
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


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
@override_settings(
    DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-rate-current-finalizer-pg-tests-")
)
class RateCurrentDateFinalizerPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def test_one_account_exact_due_run_race_retains_one_replayable_decision(self):
        fixture, _successor = self._due_fixture()
        outcomes = self._publication_race(
            (fixture.maker.pk, fixture.account.pk, "pg-finalizer-exact"),
            (fixture.maker.pk, fixture.account.pk, "pg-finalizer-exact"),
        )

        self.assertEqual(sorted(outcomes), ["replayed", "success"])
        self._assert_one_effect(fixture.account.pk)

    def test_one_account_changed_key_race_retains_one_winner(self):
        fixture, _successor = self._due_fixture()
        outcomes = self._publication_race(
            (fixture.maker.pk, fixture.account.pk, "pg-finalizer-changed-a"),
            (fixture.maker.pk, fixture.account.pk, "pg-finalizer-changed-b"),
        )

        self.assertEqual(sorted(outcomes), ["conflict", "success"])
        self._assert_one_effect(fixture.account.pk)

    def test_cross_account_key_race_binds_key_to_one_account(self):
        fixture = build_servicing_owner_fixture(suffix=uuid4().hex[:8])
        other_account = clone_servicing_account(
            fixture=fixture, suffix=uuid4().hex[:8]
        )
        self._activate_due_rates(fixture)
        manager = self._portfolio_manager()
        outcomes = self._publication_race(
            (manager.pk, fixture.account.pk, "pg-finalizer-cross-account"),
            (manager.pk, other_account.pk, "pg-finalizer-cross-account"),
        )

        self.assertEqual(sorted(outcomes), ["conflict", "success"])
        from sfpcl_credit.configurations.models import CurrentRateProjectionDecision

        self.assertEqual(CurrentRateProjectionDecision.objects.count(), 1)

    def test_bounded_portfolio_runs_converge_every_stale_account_once(self):
        fixture = build_servicing_owner_fixture(suffix=uuid4().hex[:8])
        other_accounts = [
            clone_servicing_account(fixture=fixture, suffix=uuid4().hex[:8])
            for _index in range(2)
        ]
        self._activate_due_rates(fixture)
        from sfpcl_credit.configurations.models import CurrentRateProjectionDecision
        from sfpcl_credit.configurations.modules.interest_rate_configuration import (
            run_due_current_rate_projections,
        )

        with patch(
            "sfpcl_credit.configurations.modules.interest_rate_configuration.timezone.localdate",
            return_value=date(2026, 9, 1),
        ):
            first = run_due_current_rate_projections(limit=2)
            second = run_due_current_rate_projections(limit=2)
            repeated = run_due_current_rate_projections(limit=2)

        self.assertEqual([len(first), len(second), len(repeated)], [2, 1, 0])
        self.assertEqual(CurrentRateProjectionDecision.objects.count(), 3)
        for account in [fixture.account, *other_accounts]:
            account.refresh_from_db()
            self.assertEqual(f"{account.current_interest_rate:.4f}", "9.7500")

    def test_competing_portfolio_runs_keep_stale_account_visible_and_singular(self):
        fixture = build_servicing_owner_fixture(suffix=uuid4().hex[:8])
        other_account = clone_servicing_account(
            fixture=fixture, suffix=uuid4().hex[:8]
        )
        self._activate_due_rates(fixture)
        restore_servicing_account_to_created_read_state(fixture=fixture)
        barrier = Barrier(2)

        def contender():
            from sfpcl_credit.configurations.modules.interest_rate_configuration import (
                run_due_current_rate_projections,
            )

            close_old_connections()
            try:
                barrier.wait(timeout=15)
                return [
                    projection.loan_account_id
                    for projection in run_due_current_rate_projections(limit=2)
                ]
            finally:
                connections["default"].close()

        with patch(
            "sfpcl_credit.configurations.modules.interest_rate_configuration.timezone.localdate",
            return_value=date(2026, 9, 1),
        ):
            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = list(pool.map(lambda _item: contender(), range(2)))

        self.assertEqual(
            {account_id for outcome in outcomes for account_id in outcome},
            {fixture.account.pk, other_account.pk},
        )
        from sfpcl_credit.configurations.models import CurrentRateProjectionDecision
        from sfpcl_credit.processes.loan_account_360 import list_accounts

        self.assertEqual(CurrentRateProjectionDecision.objects.count(), 2)
        reader = User.objects.create(
            full_name="PG Rate Finalizer Portfolio Reader",
            email=f"pg.rate.reader.{uuid4().hex[:8]}@sfpcl.example",
            status="active",
            primary_role=Role.objects.get(role_code="accounts_head"),
        )
        with patch(
            "sfpcl_credit.configurations.modules.interest_rate_configuration.timezone.localdate",
            return_value=date(2026, 9, 1),
        ):
            rows, pagination = list_accounts(actor=reader, query_params={})
        self.assertEqual(pagination["total_count"], 1)
        self.assertIn(str(fixture.account.pk), {row["loan_account_id"] for row in rows})
        self.assertEqual(rows[0]["current_interest_rate"], "9.7500")
        other_account.refresh_from_db()
        self.assertEqual(f"{other_account.current_interest_rate:.4f}", "9.7500")

    def _due_fixture(self):
        fixture = build_servicing_owner_fixture(suffix=uuid4().hex[:8])
        successor = self._activate_due_rates(fixture)
        return fixture, successor

    def _activate_due_rates(self, fixture):
        current = build_interest_rate_proposal(
            fixture=fixture,
            version=f"PG-CURRENT-{uuid4().hex[:8]}",
            effective_from=date(2026, 7, 1),
            rate="9.2500",
        )
        activate_interest_rate(
            fixture=fixture,
            proposal=current,
            idempotency_key=f"pg-current-{current.pk}",
        )
        successor = build_interest_rate_proposal(
            fixture=fixture,
            version=f"PG-DUE-{uuid4().hex[:8]}",
            effective_from=date(2026, 9, 1),
            rate="9.7500",
        )
        activate_interest_rate(
            fixture=fixture,
            proposal=successor,
            idempotency_key=f"pg-due-{successor.pk}",
        )
        return successor

    def _portfolio_manager(self):
        role = Role.objects.get(role_code="accounts_head")
        permission = Permission.objects.get(
            permission_code="config.interest_rate.manage"
        )
        RolePermission.objects.get_or_create(role=role, permission=permission)
        return User.objects.create(
            full_name="PG Current Rate Portfolio Manager",
            email=f"pg.rate.manager.{uuid4().hex[:8]}@sfpcl.example",
            status="active",
            primary_role=role,
        )

    def _publication_race(self, *items):
        barrier = Barrier(len(items))

        def contender(item):
            from sfpcl_credit.configurations.modules.interest_rate_configuration import (
                publish_current_rate_projection,
            )

            close_old_connections()
            try:
                actor = User.objects.get(pk=item[0])
                barrier.wait(timeout=15)
                try:
                    result = publish_current_rate_projection(
                        actor=actor,
                        request=None,
                        loan_account_id=item[1],
                        idempotency_key=item[2],
                    )
                    return "replayed" if result.idempotency_replayed else "success"
                except InterestRateConflict:
                    return "conflict"
            finally:
                connections["default"].close()

        with patch(
            "sfpcl_credit.configurations.modules.interest_rate_configuration.timezone.localdate",
            return_value=date(2026, 9, 1),
        ):
            with ThreadPoolExecutor(max_workers=len(items)) as pool:
                return list(pool.map(contender, items))

    def _assert_one_effect(self, account_id):
        from sfpcl_credit.configurations.models import CurrentRateProjectionDecision

        self.assertEqual(
            CurrentRateProjectionDecision.objects.filter(
                loan_account_id=account_id
            ).count(),
            1,
        )
        self.assertEqual(
            AuditLog.objects.filter(
                action="config.interest_rate.loan_projection_converged",
                entity_id=account_id,
            ).count(),
            1,
        )
