from datetime import datetime, timezone

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class CommunicationReceiptOwnerMigrationTests(TransactionTestCase):
    reset_sequences = True

    migrate_from = [
        ("communications", "0003_notification"),
        (
            "disbursements",
            "0007_remove_disbursement_disb_success_evidence_complete_and_more",
        ),
    ]
    migrate_to = [
        ("communications", "0004_advice_outbox_and_receipt_owner"),
        (
            "disbursements",
            "0007_remove_disbursement_disb_success_evidence_complete_and_more",
        ),
    ]

    def test_receipt_row_and_schema_survive_forward_reverse_and_reapply(self):
        from sfpcl_credit.tests.test_disbursement_advice_api import (
            DisbursementAdviceApiTests,
        )

        self._migrate(self.migrate_from)
        fixture = DisbursementAdviceApiTests(
            "test_public_success_sends_exact_advice_without_financial_side_effects"
        )
        fixture.setUp()

        old_apps = MigrationExecutor(connection).loader.project_state(
            self.migrate_from
        ).apps
        OldReceipt = old_apps.get_model(
            "disbursements", "DisbursementAdviceDeliveryReceipt"
        )
        retained = OldReceipt.objects.create(
            advice_intent_id=fixture.row.advice_intent.pk,
            idempotency_key="migration-receipt-owner-key",
            payload_digest="a" * 64,
            external_message_id="manual-migration-receipt-owner",
            delivery_status="sent",
            accepted_at=datetime(2026, 7, 18, 8, 50, tzinfo=timezone.utc),
            created_at=datetime(2026, 7, 18, 8, 51, tzinfo=timezone.utc),
        )
        retained_id = str(retained.pk)
        retained_values = self._receipt_values(OldReceipt)
        before = self._receipt_signature()

        moved_apps = self._migrate(self.migrate_to)
        MovedReceipt = moved_apps.get_model(
            "communications", "DisbursementAdviceDeliveryReceipt"
        )
        self.assertEqual(str(MovedReceipt.objects.get().pk), retained_id)
        self.assertEqual(self._receipt_values(MovedReceipt), retained_values)
        self.assertEqual(self._receipt_signature(), before)
        self.assertEqual(self._outbox_table_count(), 1)

        reversed_apps = self._migrate(self.migrate_from)
        ReversedReceipt = reversed_apps.get_model(
            "disbursements", "DisbursementAdviceDeliveryReceipt"
        )
        self.assertEqual(str(ReversedReceipt.objects.get().pk), retained_id)
        self.assertEqual(self._receipt_values(ReversedReceipt), retained_values)
        self.assertEqual(self._receipt_signature(), before)
        self.assertEqual(self._outbox_table_count(), 0)

        reapplied_apps = self._migrate(self.migrate_to)
        ReappliedReceipt = reapplied_apps.get_model(
            "communications", "DisbursementAdviceDeliveryReceipt"
        )
        self.assertEqual(str(ReappliedReceipt.objects.get().pk), retained_id)
        self.assertEqual(self._receipt_values(ReappliedReceipt), retained_values)
        self.assertEqual(self._receipt_signature(), before)
        self.assertEqual(self._outbox_table_count(), 1)

    def _migrate(self, targets):
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    def _receipt_signature(self):
        table = "disbursement_advice_delivery_receipts"
        with connection.cursor() as cursor:
            constraints = connection.introspection.get_constraints(cursor, table)
            description = connection.introspection.get_table_description(
                cursor, table
            )
        return {
            "table": table,
            "columns": tuple(field.name for field in description),
            "constraints": tuple(sorted(constraints)),
        }

    def _receipt_values(self, model):
        row = model.objects.values(
            "delivery_receipt_id",
            "advice_intent_id",
            "idempotency_key",
            "payload_digest",
            "external_message_id",
            "delivery_status",
            "accepted_at",
            "created_at",
        ).get()
        return {
            **row,
            "delivery_receipt_id": str(row["delivery_receipt_id"]),
            "advice_intent_id": str(row["advice_intent_id"]),
        }

    def _outbox_table_count(self):
        return connection.introspection.table_names().count(
            "communication_delivery_outboxes"
        )
