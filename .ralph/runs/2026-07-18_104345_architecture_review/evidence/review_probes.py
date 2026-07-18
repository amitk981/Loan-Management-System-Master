"""Review-only probes for architecture review 2026-07-18_104345.

This module lives outside product/test discovery. The architecture review loads
the two named methods explicitly against an isolated Django test database.
"""

from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

from sfpcl_credit.communications.adapters import FakeEmailDeliveryAdapter
from sfpcl_credit.communications.models import CommunicationDeliveryOutbox
from sfpcl_credit.disbursements.modules.disbursement_workflow import (
    DisbursementAdviceConflict,
    DisbursementWorkflow,
)
from sfpcl_credit.shared.migration_state_guard import (
    legal_checklist_state_ownership_violations,
)
from sfpcl_credit.tests.test_disbursement_advice_api import (
    DisbursementAdviceApiTests,
)


class LegacyAdviceOutboxReplayProbe(DisbursementAdviceApiTests):
    def test_terminal_advice_without_outbox_never_reinvokes_provider_or_rewrites_outbox(self):
        first = self._post()
        self.assertEqual(first.status_code, 200, first.content)
        CommunicationDeliveryOutbox.objects.get(
            advice_intent=self.row.advice_intent
        ).delete()

        class CountingAdapter(FakeEmailDeliveryAdapter):
            calls = 0

            def send_email(self, payload, idempotency_key):
                self.calls += 1
                return super().send_email(payload, idempotency_key)

        adapter = CountingAdapter()
        with patch(
            "sfpcl_credit.communications.modules.communication_dispatcher."
            "ManualEmailDeliveryAdapter",
            return_value=adapter,
        ):
            replay = self._post()

        self.assertEqual(replay.status_code, 409, replay.content)
        self.assertEqual(
            (
                adapter.calls,
                CommunicationDeliveryOutbox.objects.filter(
                    advice_intent=self.row.advice_intent
                ).count(),
            ),
            (0, 0),
            "terminal/legacy advice must fail closed before dispatch or outbox rewrite",
        )


class ProviderTupleMutationProbe(DisbursementAdviceApiTests):
    def test_changed_valid_provider_tuple_cannot_become_terminal_delivery_truth(self):
        class RecordingAdapter(FakeEmailDeliveryAdapter):
            calls = 0

            def send_email(self, payload, idempotency_key):
                self.calls += 1
                return super().send_email(payload, idempotency_key)

        adapter = RecordingAdapter()
        with patch(
            "sfpcl_credit.communications.modules.communication_dispatcher."
            "_retained_receipt",
            side_effect=RuntimeError("forced pre-receipt crash"),
        ):
            with self.assertRaisesRegex(RuntimeError, "pre-receipt"):
                DisbursementWorkflow.send_advice(
                    actor=self.actor,
                    disbursement_id=self.row.pk,
                    payload={
                        "channel": "email",
                        "recipient_email": "borrower.advice@example.com",
                    },
                    adapter=adapter,
                )

        outbox = CommunicationDeliveryOutbox.objects.get(
            advice_intent=self.row.advice_intent
        )
        CommunicationDeliveryOutbox.objects.filter(pk=outbox.pk).update(
            provider_external_message_id=(
                "manual:00000000-0000-4000-8000-000000000001"
            ),
            provider_accepted_at=outbox.provider_accepted_at + timedelta(seconds=1),
        )

        with self.assertRaises(DisbursementAdviceConflict):
            DisbursementWorkflow.send_advice(
                actor=self.actor,
                disbursement_id=self.row.pk,
                payload={
                    "channel": "email",
                    "recipient_email": "borrower.advice@example.com",
                },
                adapter=adapter,
            )


class MigrationOwnershipGuardProbe(SimpleTestCase):
    def test_module_level_target_constants_cannot_bypass_cross_app_guard(self):
        synthetic = {
            Path("future_app/migrations/0001_bad.py"): """
from django.db.migrations.operations.base import Operation

TARGET_APP = "legal_documents"
TARGET_MODEL = "documentchecklist"

class BadChecklistMutation(Operation):
    def state_forwards(self, app_label, state):
        state.models[(TARGET_APP, TARGET_MODEL)].options.clear()
"""
        }

        self.assertEqual(
            legal_checklist_state_ownership_violations(sources=synthetic),
            ["future_app/migrations/0001_bad.py:BadChecklistMutation"],
        )
