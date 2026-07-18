from datetime import datetime, timezone
import hashlib
import uuid

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
        current_apps = self._migrate(
            [
                (
                    "communications",
                    "0005_advice_evidence_and_legacy_replay_closure",
                )
            ]
        )
        self.assertEqual(
            current_apps.get_model(
                "communications", "CommunicationDeliveryOutbox"
            ).objects.count(),
            0,
        )
        self.assertEqual(
            current_apps.get_model(
                "communications", "CommunicationProviderAttempt"
            ).objects.count(),
            0,
        )

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
        self._migrate(
            [
                (
                    "communications",
                    "0005_advice_evidence_and_legacy_replay_closure",
                )
            ]
        )

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
            "columns": tuple(sorted(field.name for field in description)),
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


class CommunicationAdviceEvidenceMigrationTests(TransactionTestCase):
    reset_sequences = True
    migrate_from = [("communications", "0004_advice_outbox_and_receipt_owner")]
    migrate_to = [
        ("communications", "0005_advice_evidence_and_legacy_replay_closure")
    ]

    def test_coherent_legacy_delivery_survives_forward_reverse_and_reapply(self):
        from sfpcl_credit.tests.test_disbursement_advice_api import (
            DisbursementAdviceApiTests,
        )

        old_apps = self._migrate(self.migrate_from)
        fixture = DisbursementAdviceApiTests(
            "test_public_success_sends_exact_advice_without_financial_side_effects"
        )
        fixture.setUp()
        Intent = old_apps.get_model("disbursements", "DisbursementAdviceIntent")
        Disbursement = old_apps.get_model("disbursements", "Disbursement")
        Communication = old_apps.get_model("communications", "Communication")
        Receipt = old_apps.get_model(
            "communications", "DisbursementAdviceDeliveryReceipt"
        )
        Audit = old_apps.get_model("identity", "AuditLog")
        Workflow = old_apps.get_model("workflows", "WorkflowEvent")
        action_id = uuid.uuid4()
        accepted_at = datetime(2026, 7, 18, 9, 30, tzinfo=timezone.utc)
        communication_id = fixture.row.advice_intent.pk
        audit = Audit.objects.create(
            actor_user_id=fixture.actor.pk,
            actor_type="user",
            action="disbursement.advice_sent",
            entity_type="disbursement",
            entity_id=fixture.row.pk,
            old_value_json={"disbursement_advice_communication_id": None},
            new_value_json={
                "action_id": str(action_id),
                "communication_id": str(communication_id),
            },
        )
        workflow = Workflow.objects.create(
            workflow_name="DisbursementAdviceSent",
            entity_type="disbursement",
            entity_id=fixture.row.pk,
            from_state="transfer_successful",
            to_state="advice_sent",
            triggered_by_user_id=fixture.actor.pk,
            trigger_reason=(
                f"action_id={action_id};communication_id={communication_id}"
            ),
        )
        Intent.objects.filter(pk=communication_id).update(
            delivery_status="sent",
            delivery_action_id=action_id,
            delivery_evidence_digest="e" * 64,
            delivery_audit_id=audit.pk,
            delivery_workflow_event_id=workflow.pk,
        )
        Communication.objects.create(
            communication_id=communication_id,
            related_entity_type="disbursement",
            related_entity_id=fixture.row.pk,
            recipient_party_type="borrower",
            recipient_party_id=fixture.row.member_id,
            recipient_address="borrower.advice@example.com",
            channel="email",
            content_template_id=fixture.template.pk,
            subject_snapshot="Frozen legacy advice subject",
            body_snapshot="Frozen legacy advice body",
            sent_by_user_id=fixture.actor.pk,
            sent_at=accepted_at,
            delivery_status="sent",
            external_message_id="manual:coherent-legacy-advice",
        )
        Disbursement.objects.filter(pk=fixture.row.pk).update(
            disbursement_advice_communication_id=communication_id
        )
        receipt = Receipt.objects.create(
            advice_intent_id=communication_id,
            idempotency_key=f"disbursement-advice:{communication_id}",
            payload_digest="p" * 64,
            external_message_id="manual:coherent-legacy-advice",
            delivery_status="sent",
            accepted_at=accepted_at,
            created_at=accepted_at,
        )
        retained_ids = {
            "communication": str(communication_id),
            "receipt": str(receipt.pk),
            "audit": str(audit.pk),
            "workflow": str(workflow.pk),
            "action": str(action_id),
        }
        receipt_before = self._manifest("disbursement_advice_delivery_receipts")
        outbox_before = self._manifest("communication_delivery_outboxes")

        current_apps = self._migrate(self.migrate_to)
        first = self._current_values(current_apps)
        self.assertEqual(first["retained_ids"], retained_ids)
        self.assertEqual(first["outbox_id"], retained_ids["communication"])
        self.assertEqual(first["adapter_kind"], "legacy:pre-outbox")
        self.assertEqual(first["provider_outcome"], "accepted")
        self.assertEqual(first["template_name"], fixture.template.template_name)
        self.assertEqual(first["template_variables"], sorted(fixture.template.variables_json))
        self.assertEqual(first["primitive_outbox_intent"], retained_ids["communication"])
        self.assertEqual(first["primitive_receipt_intent"], retained_ids["communication"])
        receipt_after = self._manifest("disbursement_advice_delivery_receipts")
        forward_manifests = {
            table: self._manifest(table)
            for table in (
                "disbursement_advice_delivery_receipts",
                "communication_delivery_outboxes",
                "communication_provider_attempts",
            )
        }
        self.assertEqual(receipt_after["columns"], receipt_before["columns"])
        self.assertFalse(
            any(
                (value.get("foreign_key") or (None,))[0]
                == "disbursement_advice_intents"
                for value in receipt_after["constraints"].values()
            )
        )

        reversed_apps = self._migrate(self.migrate_from)
        self.assertEqual(
            reversed_apps.get_model(
                "communications", "DisbursementAdviceDeliveryReceipt"
            ).objects.count(),
            1,
        )
        self.assertEqual(
            reversed_apps.get_model(
                "communications", "CommunicationDeliveryOutbox"
            ).objects.count(),
            0,
        )
        self.assertNotIn(
            "communication_provider_attempts",
            connection.introspection.table_names(),
        )
        self.assertEqual(
            self._manifest("disbursement_advice_delivery_receipts"),
            receipt_before,
        )
        self.assertEqual(
            self._manifest("communication_delivery_outboxes"), outbox_before
        )

        reapplied_apps = self._migrate(self.migrate_to)
        self.assertEqual(self._current_values(reapplied_apps), first)
        self.assertEqual(
            {
                table: self._manifest(table)
                for table in (
                    "disbursement_advice_delivery_receipts",
                    "communication_delivery_outboxes",
                    "communication_provider_attempts",
                )
            },
            forward_manifests,
        )

    def test_accepted_pending_and_no_advice_rows_reapply_without_fabrication(self):
        from sfpcl_credit.tests.test_disbursement_advice_api import (
            DisbursementAdviceApiTests,
        )

        old_apps = self._migrate(self.migrate_from)
        fixture = DisbursementAdviceApiTests(
            "test_public_success_sends_exact_advice_without_financial_side_effects"
        )
        fixture.setUp()
        Outbox = old_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        )
        accepted_at = datetime(2026, 7, 18, 10, 30, tzinfo=timezone.utc)
        accepted_id = uuid.uuid4()
        accepted = Outbox.objects.create(
            outbox_id=accepted_id,
            advice_intent_id=fixture.row.advice_intent.pk,
            communication_id=fixture.row.advice_intent.pk,
            idempotency_key=f"disbursement-advice:{fixture.row.advice_intent.pk}",
            channel="email",
            recipient_address="borrower.advice@example.com",
            recipient_digest=hashlib.sha256(
                b"borrower.advice@example.com"
            ).hexdigest(),
            content_template_id=fixture.template.pk,
            template_code_snapshot=fixture.template.template_code,
            template_version_snapshot=fixture.template.template_version,
            template_checksum_sha256="t" * 64,
            subject_snapshot="Accepted crash subject",
            body_snapshot="Accepted crash body",
            payload_digest="d" * 64,
            related_entity_type="disbursement",
            related_entity_id=fixture.row.pk,
            delivery_status="sent",
            provider_external_message_id="manual:accepted-not-finalized",
            provider_delivery_status="sent",
            provider_accepted_at=accepted_at,
            created_at=accepted_at,
        )
        accepted_values = dict(
            Outbox.objects.values(
                "outbox_id",
                "advice_intent_id",
                "communication_id",
                "idempotency_key",
                "payload_digest",
                "provider_external_message_id",
                "provider_delivery_status",
                "provider_accepted_at",
            ).get(pk=accepted.pk)
        )

        current_apps = self._migrate(self.migrate_to)
        CurrentOutbox = current_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        )
        Attempt = current_apps.get_model(
            "communications", "CommunicationProviderAttempt"
        )
        current = CurrentOutbox.objects.get(pk=accepted_id)
        self.assertEqual(current.accepted_provider_attempt_id, Attempt.objects.get().pk)
        self.assertEqual(Attempt.objects.get().adapter_kind, "legacy:retained-outbox")
        self.assertEqual(current.template_name_snapshot, fixture.template.template_name)

        reversed_apps = self._migrate(self.migrate_from)
        ReversedOutbox = reversed_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        )
        reversed_values = dict(
            ReversedOutbox.objects.values(*accepted_values).get(pk=accepted_id)
        )
        self.assertEqual(reversed_values, accepted_values)
        ReversedOutbox.objects.filter(pk=accepted_id).delete()
        pending_id = uuid.uuid4()
        pending_values = {
            **accepted_values,
            "outbox_id": pending_id,
            "delivery_status": "pending",
            "provider_external_message_id": None,
            "provider_delivery_status": None,
            "provider_accepted_at": None,
        }
        ReversedOutbox.objects.create(
            **pending_values,
            channel="email",
            recipient_address="borrower.advice@example.com",
            recipient_digest=hashlib.sha256(
                b"borrower.advice@example.com"
            ).hexdigest(),
            content_template_id=fixture.template.pk,
            template_code_snapshot=fixture.template.template_code,
            template_version_snapshot=fixture.template.template_version,
            template_checksum_sha256="t" * 64,
            subject_snapshot="Pending subject",
            body_snapshot="Pending body",
            related_entity_type="disbursement",
            related_entity_id=fixture.row.pk,
            created_at=accepted_at,
        )

        pending_apps = self._migrate(self.migrate_to)
        PendingOutbox = pending_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        )
        self.assertEqual(PendingOutbox.objects.get().delivery_status, "pending")
        self.assertEqual(
            pending_apps.get_model(
                "communications", "CommunicationProviderAttempt"
            ).objects.count(),
            0,
        )
        no_advice_apps = self._migrate(self.migrate_from)
        no_advice_apps.get_model(
            "communications", "CommunicationDeliveryOutbox"
        ).objects.all().delete()
        final_apps = self._migrate(self.migrate_to)
        self.assertEqual(
            final_apps.get_model(
                "communications", "CommunicationDeliveryOutbox"
            ).objects.count(),
            0,
        )
        self.assertEqual(
            final_apps.get_model(
                "communications", "CommunicationProviderAttempt"
            ).objects.count(),
            0,
        )

    def _migrate(self, targets):
        executor = MigrationExecutor(connection)
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    def _current_values(self, apps):
        Outbox = apps.get_model("communications", "CommunicationDeliveryOutbox")
        Attempt = apps.get_model("communications", "CommunicationProviderAttempt")
        Receipt = apps.get_model(
            "communications", "DisbursementAdviceDeliveryReceipt"
        )
        Communication = apps.get_model("communications", "Communication")
        Intent = apps.get_model("disbursements", "DisbursementAdviceIntent")
        outbox = Outbox.objects.get()
        attempt = Attempt.objects.get()
        receipt = Receipt.objects.get()
        intent = Intent.objects.get(pk=outbox.advice_intent)
        return {
            "retained_ids": {
                "communication": str(
                    Communication.objects.get(pk=outbox.communication_id).pk
                ),
                "receipt": str(receipt.pk),
                "audit": str(intent.delivery_audit_id),
                "workflow": str(intent.delivery_workflow_event_id),
                "action": str(intent.delivery_action_id),
            },
            "outbox_id": str(outbox.pk),
            "attempt_id": str(attempt.pk),
            "adapter_kind": attempt.adapter_kind,
            "provider_outcome": attempt.outcome,
            "template_name": outbox.template_name_snapshot,
            "template_variables": outbox.template_variables_snapshot,
            "primitive_outbox_intent": str(outbox.advice_intent),
            "primitive_receipt_intent": str(receipt.advice_intent),
        }

    def _manifest(self, table):
        with connection.cursor() as cursor:
            description = connection.introspection.get_table_description(
                cursor, table
            )
            constraints = connection.introspection.get_constraints(cursor, table)
            objects = ()
            if connection.vendor == "sqlite":
                cursor.execute(
                    "SELECT type, name, sql FROM sqlite_master "
                    "WHERE tbl_name = %s AND sql IS NOT NULL ORDER BY type, name",
                    [table],
                )
                objects = tuple(cursor.fetchall())
        return {
            "table": table,
            "columns": tuple(sorted(
                (
                    field.name,
                    str(field.type_code),
                    field.null_ok,
                    field.default,
                )
                for field in description
            )),
            "constraints": {
                name: {
                    key: tuple(value) if isinstance(value, list) else value
                    for key, value in sorted(details.items())
                }
                for name, details in sorted(constraints.items())
            },
            "definitions": objects,
        }
