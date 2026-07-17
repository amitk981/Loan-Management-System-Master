import ast
import inspect
import uuid

from django.apps import apps
from django.test import SimpleTestCase

from sfpcl_credit.communications.adapters import (
    EmailDeliveryPayload,
    EmailDeliveryResult,
    FakeEmailDeliveryAdapter,
    FutureEmailDeliveryAdapter,
    ManualEmailDeliveryAdapter,
)
from sfpcl_credit.communications import adapters as communication_adapters
from sfpcl_credit.communications import models as communication_models
from sfpcl_credit.communications.models import (
    CommunicationDeliveryOutbox,
    DisbursementAdviceDeliveryReceipt,
)
from sfpcl_credit.disbursements.models import (
    DisbursementAdviceDeliveryReceipt as LegacyDeliveryReceipt,
)


class CommunicationAdvicePersistenceOwnershipTests(SimpleTestCase):
    def test_communications_owns_complete_outbox_and_retained_receipt_state(self):
        outbox = CommunicationDeliveryOutbox._meta
        self.assertEqual(outbox.app_label, "communications")
        self.assertEqual(outbox.db_table, "communication_delivery_outboxes")
        self.assertTrue(outbox.get_field("advice_intent").one_to_one)
        self.assertTrue(outbox.get_field("communication_id").unique)
        self.assertTrue(outbox.get_field("idempotency_key").unique)
        self.assertEqual(
            {
                "channel",
                "recipient_address",
                "recipient_digest",
                "template_code_snapshot",
                "template_version_snapshot",
                "template_checksum_sha256",
                "subject_snapshot",
                "body_snapshot",
                "payload_digest",
                "related_entity_type",
                "related_entity_id",
                "delivery_status",
                "provider_external_message_id",
                "provider_delivery_status",
                "provider_accepted_at",
            }
            - {field.name for field in outbox.fields},
            set(),
        )

        receipt = DisbursementAdviceDeliveryReceipt._meta
        self.assertEqual(receipt.app_label, "communications")
        self.assertEqual(receipt.db_table, "disbursement_advice_delivery_receipts")
        self.assertEqual(receipt.pk.name, "delivery_receipt_id")
        self.assertTrue(receipt.get_field("advice_intent").one_to_one)
        self.assertTrue(receipt.get_field("idempotency_key").unique)
        self.assertTrue(receipt.get_field("external_message_id").unique)
        self.assertIn(
            "advice_delivery_receipt_complete",
            {constraint.name for constraint in receipt.constraints},
        )
        self.assertIs(LegacyDeliveryReceipt, DisbursementAdviceDeliveryReceipt)
        self.assertIs(
            apps.get_model("communications", "DisbursementAdviceDeliveryReceipt"),
            DisbursementAdviceDeliveryReceipt,
        )
        self.assertNotIn(
            "disbursementadvicedeliveryreceipt",
            apps.all_models["disbursements"],
        )

    def test_communications_persistence_and_adapters_have_no_disbursement_import(self):
        for module in (communication_models, communication_adapters):
            tree = ast.parse(inspect.getsource(module))
            imported_modules = {
                node.module
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module
            }
            imported_modules.update(
                name.name
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for name in node.names
            )
            self.assertFalse(
                any(
                    imported.startswith("sfpcl_credit.disbursements")
                    for imported in imported_modules
                ),
                f"{module.__name__} imports disbursement policy/models",
            )


class AdviceEmailAdapterContractTests(SimpleTestCase):
    def test_manual_fake_and_future_use_stable_key_identity_across_fresh_instances(self):
        first = self._payload(subject="First subject")
        changed = self._payload(subject="Changed subject")
        key = "disbursement-advice:stable-intent"
        factories = (
            ManualEmailDeliveryAdapter,
            FakeEmailDeliveryAdapter,
            lambda: FutureEmailDeliveryAdapter(
                transport=FakeEmailDeliveryAdapter()
            ),
        )

        for factory in factories:
            with self.subTest(adapter=factory):
                accepted = factory().send_email(first, key)
                exact_replay = factory().send_email(first, key)
                changed_replay = factory().send_email(changed, key)
                self.assertIsInstance(accepted, EmailDeliveryResult)
                self.assertEqual(
                    exact_replay.external_message_id,
                    accepted.external_message_id,
                )
                self.assertEqual(
                    changed_replay.external_message_id,
                    accepted.external_message_id,
                )
                self.assertEqual(changed_replay.delivery_status, "sent")

    def test_future_provider_rejection_is_retryable_without_fabricated_acceptance(self):
        class RejectOnceTransport:
            def __init__(self):
                self.attempts = 0
                self.accepting = FakeEmailDeliveryAdapter()

            def send_email(self, payload, idempotency_key):
                self.attempts += 1
                if self.attempts == 1:
                    raise ValueError("provider rejected")
                return self.accepting.send_email(payload, idempotency_key)

        transport = RejectOnceTransport()
        adapter = FutureEmailDeliveryAdapter(transport=transport)
        payload = self._payload(subject="Retryable advice")
        key = "disbursement-advice:retryable-intent"

        with self.assertRaisesRegex(ValueError, "provider rejected"):
            adapter.send_email(payload, key)
        accepted = adapter.send_email(payload, key)

        self.assertEqual(transport.attempts, 2)
        self.assertEqual(accepted.delivery_status, "sent")

    def _payload(self, *, subject):
        return EmailDeliveryPayload(
            communication_id=uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
            recipient_email="borrower@example.com",
            subject=subject,
            body_text="Protected advice body",
            related_entity_type="disbursement",
            related_entity_id=uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        )
