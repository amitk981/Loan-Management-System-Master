from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from unittest import skipUnless
from unittest.mock import patch
import uuid

from django.db import IntegrityError, close_old_connections, connection, connections, models
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.test import Client, TestCase, TransactionTestCase
from django.http import JsonResponse
from django.utils import timezone

from sfpcl_credit.communications.adapters import (
    FakeEmailDeliveryAdapter,
    FutureEmailDeliveryAdapter,
)
from sfpcl_credit.communications.models import (
    Communication,
    CommunicationDeliveryOutbox,
    CommunicationDeliveryJob,
    CommunicationProviderAttempt,
    ContentTemplate,
    DisbursementAdviceDeliveryReceipt,
)
from sfpcl_credit.communications.modules.communication_dispatcher import (
    CommunicationDispatcher,
)
from sfpcl_credit.disbursements.models import (
    BankTransfer,
    Disbursement,
    LoanRegisterUpdate,
)
from sfpcl_credit.disbursements.modules.disbursement_workflow import (
    DisbursementAdviceConflict,
)
from sfpcl_credit.processes.disbursement_advice_delivery import (
    queue_disbursement_advice,
    send_disbursement_advice_now,
)
from sfpcl_credit.identity.models import AuditLog, Permission, RolePermission, User
from sfpcl_credit.legal_documents.models import DocumentChecklist
from sfpcl_credit.loans.models import LoanAccount
from sfpcl_credit.tests.api_contracts import assert_success_envelope
from sfpcl_credit.tests import test_disbursement_transfer_success_api as transfer_fixtures
from sfpcl_credit.tracer.models import Repayment
from sfpcl_credit.workflows.models import WorkflowEvent


ADVICE_VARIABLES = [
    "borrower_name",
    "application_reference_number",
    "loan_account_number",
    "sanctioned_amount",
    "disbursement_amount",
    "disbursed_at",
    "bank_reference_number",
]


def _send_advice_through_process(**kwargs):
    queue_disbursement_advice(
        actor=kwargs["actor"],
        disbursement_id=kwargs["disbursement_id"],
        payload=kwargs["payload"],
        request=kwargs.get("request"),
        idempotency_key=f"advice-test:{kwargs['disbursement_id']}",
    )
    return send_disbursement_advice_now(**kwargs)


class DisbursementAdviceApiTests(TestCase):
    def setUp(self):
        owner = transfer_fixtures.DisbursementTransferSuccessApiTests(
            "test_public_success_records_transfer_and_activates_exact_loan_atomically"
        )
        owner.setUp()
        transferred = owner._post(
            bank_reference_number="RBL-ADVICE-9876",
            disbursed_at=timezone.now(),
        )
        self.assertEqual(transferred.status_code, 200, transferred.content)
        finance_actor = owner.owner.fixture.actor
        owner.owner.fixture.fixture._grant(
            finance_actor, "finance.disbursement.send_advice"
        )
        Permission.objects.filter(
            permission_code="finance.disbursement.send_advice"
        ).update(risk_level=Permission.RISK_HIGH)
        self.owner = owner
        self.actor = finance_actor
        self.client = Client()
        self.row = Disbursement.objects.select_related(
            "member", "loan_application", "loan_account"
        ).get(pk=owner.owner.disbursement_id)
        self.row.member.email = "Borrower.Advice@Example.com"
        self.row.member.save(update_fields=["email"])
        self.setUp_template()

    def test_public_role_matrix_allows_scoped_credit_manager_and_denies_cfc_only(
        self,
    ):
        credit_manager = self.owner.owner.fixture.fixture._user(
            "credit_manager", "Advice Credit Manager"
        )
        self.owner.owner.fixture.fixture._grant(
            credit_manager, "finance.disbursement.send_advice"
        )
        cfc = self.owner.owner.cfc
        self.owner.owner.fixture.fixture._grant(
            cfc, "finance.disbursement.send_advice"
        )

        denied = self._post(actor=cfc)

        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(denied.json()["error"]["code"], "OBJECT_ACCESS_DENIED")

        LoanAccount.objects.filter(pk=self.row.loan_account_id).update(
            loan_account_status="sanctioned"
        )
        wrong_active_loan_scope = self._post(actor=credit_manager)
        self.assertEqual(wrong_active_loan_scope.status_code, 403)
        LoanAccount.objects.filter(pk=self.row.loan_account_id).update(
            loan_account_status="active"
        )

        credit_manager.approval_authority_type = "chief_financial_controller"
        credit_manager.save(update_fields=["approval_authority_type"])
        accepted = self._post(actor=credit_manager)

        self.assertEqual(accepted.status_code, 200, accepted.content)
        self.assertEqual(accepted.json()["data"]["delivery_status"], "sent")
        self.assertEqual(
            AuditLog.objects.get(action="disbursement.advice_sent")
            .new_value_json["actor_role_code"],
            "credit_manager",
        )

    def test_public_success_sends_exact_advice_without_financial_side_effects(self):
        account_before = LoanAccount.objects.values().get(pk=self.row.loan_account_id)
        checklist_before = list(DocumentChecklist.objects.values())
        repayment_count = Repayment.objects.count()

        response = self._post()

        self.assertEqual(response.status_code, 200, response.content)
        assert_success_envelope(self, response.json())
        data = response.json()["data"]
        self.assertEqual(data["disbursement_id"], str(self.row.pk))
        self.assertEqual(data["delivery_status"], "sent")
        self.assertTrue(data["sent_at"].endswith("Z"))
        communication = Communication.objects.get(
            communication_id=data["disbursement_advice_communication_id"]
        )
        self.row.refresh_from_db()
        self.assertEqual(
            self.row.disbursement_advice_communication_id, communication.pk
        )
        self.assertEqual(communication.recipient_address, "borrower.advice@example.com")
        self.assertEqual(communication.recipient_party_type, "borrower")
        self.assertEqual(communication.recipient_party_id, self.row.member_id)
        self.assertEqual(communication.channel, "email")
        self.assertEqual(communication.content_template_id, self.template.pk)
        self.assertEqual(communication.delivery_status, "sent")
        self.assertIsNotNone(communication.external_message_id)
        self.assertIn(self.row.member.display_name, communication.body_snapshot)
        self.assertIn(
            self.row.loan_application.application_reference_number,
            communication.body_snapshot,
        )
        self.assertIn(self.row.loan_account.loan_account_number, communication.body_snapshot)
        self.assertIn("***********9876", communication.body_snapshot)
        self.assertNotIn("RBL-ADVICE-9876", communication.body_snapshot)
        audit = AuditLog.objects.get(action="disbursement.advice_sent")
        workflow = WorkflowEvent.objects.get(workflow_name="DisbursementAdviceSent")
        self.assertEqual(audit.entity_id, self.row.pk)
        self.assertEqual(workflow.entity_id, self.row.pk)
        self.assertEqual(
            audit.new_value_json["communication_id"], str(communication.pk)
        )
        self.assertNotIn("RBL-ADVICE-9876", str(audit.new_value_json))
        for protected in (
            communication.recipient_address,
            communication.subject_snapshot,
            communication.body_snapshot,
            communication.external_message_id,
            f"{self.row.disbursement_amount:.2f}",
        ):
            self.assertNotIn(protected, str(audit.new_value_json))
            self.assertNotIn(protected, workflow.trigger_reason)
        self.assertNotIn("external_message_id", audit.new_value_json)
        self.assertEqual(len(audit.new_value_json["provider_message_digest"]), 64)
        self.assertEqual(len(audit.new_value_json["subject_digest"]), 64)
        self.assertEqual(len(audit.new_value_json["body_digest"]), 64)
        self.assertEqual(
            LoanAccount.objects.values().get(pk=self.row.loan_account_id),
            account_before,
        )
        self.assertEqual(list(DocumentChecklist.objects.values()), checklist_before)
        self.assertEqual(Repayment.objects.count(), repayment_count)
        self.assertTrue(self.row.loan_register_updated_flag)

    def test_send_consumes_stable_pending_identity_and_keeps_ledgers_recipient_safe(self):
        intent = self.row.advice_intent

        response = self._post()

        self.assertEqual(response.status_code, 200, response.content)
        communication = Communication.objects.get(pk=intent.pk)
        intent.refresh_from_db()
        self.assertEqual(
            response.json()["data"]["disbursement_advice_communication_id"],
            str(intent.pk),
        )
        self.assertEqual(intent.delivery_status, "sent")
        expected_subject = self.template.subject_template.replace(
            "{{application_reference_number}}",
            self.row.loan_application.application_reference_number,
        ).replace(
            "{{loan_account_number}}", self.row.loan_account.loan_account_number
        )
        self.assertEqual(communication.subject_snapshot, expected_subject)
        audit = AuditLog.objects.get(action="disbursement.advice_sent")
        workflow = WorkflowEvent.objects.get(workflow_name="DisbursementAdviceSent")
        self.assertNotIn("borrower.advice@example.com", str(audit.new_value_json))
        self.assertNotIn("borrower.advice@example.com", workflow.trigger_reason)
        self.assertEqual(
            audit.new_value_json["recipient_masked"], "b***@example.com"
        )
        self.assertEqual(len(audit.new_value_json["recipient_digest"]), 64)

    def test_exact_replay_is_zero_write_and_changed_replay_conflicts(self):
        class CountingAdapter(FakeEmailDeliveryAdapter):
            calls = 0
            results = []

            def send_email(self, payload, idempotency_key):
                self.calls += 1
                result = super().send_email(payload, idempotency_key)
                self.results.append(result)
                return result

        adapter = CountingAdapter()
        with patch(
            "sfpcl_credit.tests.test_disbursement_advice_api."
            "FakeEmailDeliveryAdapter",
            return_value=adapter,
        ):
            first = self._post()
            self.assertEqual(first.status_code, 200, first.content)
            counts = (
                Communication.objects.count(),
                AuditLog.objects.filter(action="disbursement.advice_sent").count(),
                WorkflowEvent.objects.filter(
                    workflow_name="DisbursementAdviceSent"
                ).count(),
            )

            replay = self._post(email="  Borrower.Advice@Example.com ")
            changed_email = self._post(email="other.borrower@example.com")
            changed_channel = self.client.post(
                f"/api/v1/disbursements/{self.row.pk}/send-advice/",
                {
                    "channel": "sms",
                    "recipient_email": "borrower.advice@example.com",
                },
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY=f"advice-api:{self.row.pk}",
                **self.owner.owner.fixture._auth(self.actor),
            )

        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], first.json()["data"])
        self.assertEqual(changed_email.status_code, 409, changed_email.content)
        self.assertEqual(changed_channel.status_code, 409, changed_channel.content)
        self.assertEqual(adapter.calls, 1)
        self.assertEqual(
            (
                Communication.objects.count(),
                AuditLog.objects.filter(action="disbursement.advice_sent").count(),
                WorkflowEvent.objects.filter(
                    workflow_name="DisbursementAdviceSent"
                ).count(),
            ),
            counts,
        )

    def test_replay_conflicts_when_current_canonical_email_changes(self):
        first = self._post()
        self.assertEqual(first.status_code, 200, first.content)
        counts = self._advice_counts()
        self.row.member.email = "new.current.address@example.com"
        self.row.member.save(update_fields=["email"])

        replay = self._post()

        self.assertEqual(replay.status_code, 409, replay.content)
        self.assertEqual(self._advice_counts(), counts)

    def test_replay_conflicts_when_rendered_subject_snapshot_changes(self):
        first = self._post()
        self.assertEqual(first.status_code, 200, first.content)
        counts = self._advice_counts()
        Communication.objects.filter(
            pk=first.json()["data"]["disbursement_advice_communication_id"]
        ).update(subject_snapshot="Changed delivered subject")

        replay = self._post()

        self.assertEqual(replay.status_code, 409, replay.content)
        self.assertEqual(self._advice_counts(), counts)

    def test_fresh_adapter_retry_reuses_provider_receipt_after_post_acceptance_rollback(
        self,
    ):
        class RecordingAdapter(FakeEmailDeliveryAdapter):
            receipts = []

            def send_email(self, payload, idempotency_key):
                result = super().send_email(payload, idempotency_key)
                self.receipts.append(result)
                return result

        with patch(
            "sfpcl_credit.disbursements.modules.disbursement_advice."
            "AuditLog.objects.create",
            side_effect=RuntimeError("forced rollback after provider acceptance"),
        ):
            with self.assertRaisesRegex(RuntimeError, "forced rollback"):
                _send_advice_through_process(
                    actor=self.actor,
                    disbursement_id=self.row.pk,
                    payload={
                        "channel": "email",
                        "recipient_email": "borrower.advice@example.com",
                    },
                    adapter=RecordingAdapter(),
                )
        self._assert_no_advice_truth()
        self.row.advice_intent.refresh_from_db()
        self.assertEqual(self.row.advice_intent.delivery_status, "pending")
        self.assertFalse(
            DisbursementAdviceDeliveryReceipt.objects.filter(
                advice_intent=self.row.advice_intent.pk
            ).exists()
        )

        accepted = _send_advice_through_process(
            actor=self.actor,
            disbursement_id=self.row.pk,
            payload={
                "channel": "email",
                "recipient_email": "borrower.advice@example.com",
            },
            adapter=RecordingAdapter(),
        )

        self.assertEqual(len(RecordingAdapter.receipts), 1)
        receipt = DisbursementAdviceDeliveryReceipt.objects.get(
            advice_intent=self.row.advice_intent.pk
        )
        self.assertEqual(
            accepted["sent_at"], receipt.accepted_at.isoformat().replace("+00:00", "Z")
        )

    def test_outbox_survives_acceptance_before_receipt_and_blocks_changed_facts(self):
        class RecordingAdapter(FakeEmailDeliveryAdapter):
            results = []
            observed_outbox_statuses = []

            def send_email(self, payload, idempotency_key):
                self.observed_outbox_statuses.append(
                    CommunicationDeliveryOutbox.objects.get(
                        communication_id=payload.communication_id
                    ).delivery_status
                )
                result = super().send_email(payload, idempotency_key)
                self.results.append(result)
                return result

        with patch(
            "sfpcl_credit.communications.modules.communication_dispatcher."
            "_retained_receipt",
            side_effect=RuntimeError("forced failure before final receipt"),
        ):
            with self.assertRaisesRegex(RuntimeError, "before final receipt"):
                _send_advice_through_process(
                    actor=self.actor,
                    disbursement_id=self.row.pk,
                    payload={
                        "channel": "email",
                        "recipient_email": "borrower.advice@example.com",
                    },
                    adapter=RecordingAdapter(),
                )

        outbox = CommunicationDeliveryOutbox.objects.get(
            advice_intent=self.row.advice_intent.pk
        )
        self.assertEqual(outbox.delivery_status, "sent")
        self.assertEqual(RecordingAdapter.observed_outbox_statuses, ["pending"])
        self.assertEqual(
            outbox.provider_external_message_id,
            RecordingAdapter.results[0].external_message_id,
        )
        self.assertFalse(
            DisbursementAdviceDeliveryReceipt.objects.filter(
                advice_intent=self.row.advice_intent.pk
            ).exists()
        )
        self._assert_no_advice_truth()

        self.row.member.email = "changed.after.acceptance@example.com"
        self.row.member.save(update_fields=["email"])
        with self.assertRaises(DisbursementAdviceConflict):
            _send_advice_through_process(
                actor=self.actor,
                disbursement_id=self.row.pk,
                payload={
                    "channel": "email",
                    "recipient_email": "changed.after.acceptance@example.com",
                },
                adapter=RecordingAdapter(),
            )
        self.assertEqual(len(RecordingAdapter.results), 1)

        self.row.member.email = "Borrower.Advice@Example.com"
        self.row.member.save(update_fields=["email"])
        accepted = _send_advice_through_process(
            actor=self.actor,
            disbursement_id=self.row.pk,
            payload={
                "channel": "email",
                "recipient_email": "borrower.advice@example.com",
            },
            adapter=RecordingAdapter(),
        )

        self.assertEqual(len(RecordingAdapter.results), 1)
        self.assertEqual(accepted["delivery_status"], "sent")
        receipt = DisbursementAdviceDeliveryReceipt.objects.get(
            advice_intent=self.row.advice_intent.pk
        )
        self.assertEqual(receipt.external_message_id, outbox.provider_external_message_id)

    def test_frozen_outbox_rejects_changed_template_provenance_before_redispatch(
        self,
    ):
        class RecordingAdapter(FakeEmailDeliveryAdapter):
            results = []

            def send_email(self, payload, idempotency_key):
                result = super().send_email(payload, idempotency_key)
                self.results.append(result)
                return result

        with patch(
            "sfpcl_credit.communications.modules.communication_dispatcher."
            "_retained_receipt",
            side_effect=RuntimeError("forced failure after accepted outbox"),
        ):
            with self.assertRaisesRegex(RuntimeError, "accepted outbox"):
                _send_advice_through_process(
                    actor=self.actor,
                    disbursement_id=self.row.pk,
                    payload={
                        "channel": "email",
                        "recipient_email": "borrower.advice@example.com",
                    },
                    adapter=RecordingAdapter(),
                )

        cases = {
            "template_name": "Changed advice name",
            "template_type": "sms",
            "language_code": "mr",
            "audience": "staff",
            "template_version": "2.0",
            "approval_status": ContentTemplate.STATUS_DRAFT,
            "effective_from": timezone.localdate() + timedelta(days=1),
            "effective_to": timezone.localdate() - timedelta(days=1),
            "variables_json": [*ADVICE_VARIABLES, "unexpected"],
            "subject_template": "Changed {{borrower_name}}",
            "body_template": "Changed source {{borrower_name}}",
        }
        for field, changed in cases.items():
            with self.subTest(field=field):
                original = getattr(self.template, field)
                ContentTemplate.objects.filter(pk=self.template.pk).update(
                    **{field: changed}
                )
                with self.assertRaises(DisbursementAdviceConflict):
                    _send_advice_through_process(
                        actor=self.actor,
                        disbursement_id=self.row.pk,
                        payload={
                            "channel": "email",
                            "recipient_email": "borrower.advice@example.com",
                        },
                        adapter=RecordingAdapter(),
                    )
                ContentTemplate.objects.filter(pk=self.template.pk).update(
                    **{field: original}
                )
        self.assertEqual(len(RecordingAdapter.results), 1)

        accepted = _send_advice_through_process(
            actor=self.actor,
            disbursement_id=self.row.pk,
            payload={
                "channel": "email",
                "recipient_email": "borrower.advice@example.com",
            },
            adapter=RecordingAdapter(),
        )
        self.assertEqual(accepted["delivery_status"], "sent")
        self.assertEqual(len(RecordingAdapter.results), 1)
        self.assertEqual(
            accepted["disbursement_advice_communication_id"],
            str(self.row.advice_intent.pk),
        )

    def test_fresh_retry_recovers_before_protected_communication_commit(self):
        class RecordingAdapter(FakeEmailDeliveryAdapter):
            results = []

            def send_email(self, payload, idempotency_key):
                result = super().send_email(payload, idempotency_key)
                self.results.append(result)
                return result

        with patch(
            "sfpcl_credit.communications.modules.communication_dispatcher."
            "_create_protected_communication",
            side_effect=RuntimeError("forced failure before Communication commit"),
        ):
            with self.assertRaisesRegex(RuntimeError, "Communication commit"):
                _send_advice_through_process(
                    actor=self.actor,
                    disbursement_id=self.row.pk,
                    payload={
                        "channel": "email",
                        "recipient_email": "borrower.advice@example.com",
                    },
                    adapter=RecordingAdapter(),
                )

        outbox = CommunicationDeliveryOutbox.objects.get(
            advice_intent=self.row.advice_intent.pk
        )
        self.assertEqual(outbox.delivery_status, "sent")
        self.assertFalse(
            DisbursementAdviceDeliveryReceipt.objects.filter(
                advice_intent=self.row.advice_intent.pk
            ).exists()
        )
        self._assert_no_advice_truth()

        accepted = _send_advice_through_process(
            actor=self.actor,
            disbursement_id=self.row.pk,
            payload={
                "channel": "email",
                "recipient_email": "borrower.advice@example.com",
            },
            adapter=RecordingAdapter(),
        )

        self.assertEqual(len(RecordingAdapter.results), 1)
        self.assertEqual(accepted["delivery_status"], "sent")
        self.assertEqual(self._advice_counts(), (1, 1, 1))

    def test_accepted_outbox_malformed_provider_result_fails_closed(self):
        class RecordingAdapter(FakeEmailDeliveryAdapter):
            calls = 0

            def send_email(self, payload, idempotency_key):
                self.calls += 1
                return super().send_email(payload, idempotency_key)

        adapter = RecordingAdapter()
        with patch(
            "sfpcl_credit.communications.modules.communication_dispatcher."
            "_retained_receipt",
            side_effect=RuntimeError("forced failure after provider acceptance"),
        ):
            with self.assertRaisesRegex(RuntimeError, "provider acceptance"):
                _send_advice_through_process(
                    actor=self.actor,
                    disbursement_id=self.row.pk,
                    payload={
                        "channel": "email",
                        "recipient_email": "borrower.advice@example.com",
                    },
                    adapter=adapter,
                )
        CommunicationDeliveryOutbox.objects.filter(
            advice_intent=self.row.advice_intent.pk
        ).update(provider_external_message_id="malformed provider result")

        with self.assertRaises(DisbursementAdviceConflict):
            _send_advice_through_process(
                actor=self.actor,
                disbursement_id=self.row.pk,
                payload={
                    "channel": "email",
                    "recipient_email": "borrower.advice@example.com",
                },
                adapter=adapter,
            )

        self.assertEqual(adapter.calls, 1)
        self.assertFalse(
            DisbursementAdviceDeliveryReceipt.objects.filter(
                advice_intent=self.row.advice_intent.pk
            ).exists()
        )
        self._assert_no_advice_truth()

    def test_replay_fails_closed_when_retained_advice_evidence_changes(self):
        first = self._post()
        self.assertEqual(first.status_code, 200, first.content)
        communication_count = Communication.objects.count()
        audit = AuditLog.objects.get(action="disbursement.advice_sent")
        retained = dict(audit.new_value_json)
        AuditLog.objects.filter(pk=audit.pk).update(
            new_value_json={**retained, "template_version": "changed"}
        )

        replay = self._post()

        self.assertEqual(replay.status_code, 409, replay.content)
        self.assertEqual(Communication.objects.count(), communication_count)
        self.assertEqual(
            AuditLog.objects.filter(action="disbursement.advice_sent").count(), 1
        )

    def test_replay_conflicts_on_coordinated_provider_and_audit_drift(self):
        first = self._post()
        self.assertEqual(first.status_code, 200, first.content)
        communication = Communication.objects.get(
            pk=first.json()["data"]["disbursement_advice_communication_id"]
        )
        audit = AuditLog.objects.get(action="disbursement.advice_sent")
        evidence = dict(audit.new_value_json)
        changed_provider_id = "manual:coordinated-provider-drift"
        Communication.objects.filter(pk=communication.pk).update(
            external_message_id=changed_provider_id
        )
        AuditLog.objects.filter(pk=audit.pk).update(
            new_value_json={
                **evidence,
                "external_message_id": changed_provider_id,
            }
        )

        self.assertEqual(self._post().status_code, 409)

    def test_replay_conflicts_on_extra_unsafe_audit_evidence(self):
        first = self._post()
        self.assertEqual(first.status_code, 200, first.content)
        audit = AuditLog.objects.get(action="disbursement.advice_sent")
        AuditLog.objects.filter(pk=audit.pk).update(
            new_value_json={
                **audit.new_value_json,
                "recipient_email": "borrower.advice@example.com",
                "bank_reference_number": "RBL-ADVICE-9876",
            }
        )

        self.assertEqual(self._post().status_code, 409)

    def test_replay_conflicts_when_workflow_timestamp_changes(self):
        first = self._post()
        self.assertEqual(first.status_code, 200, first.content)
        workflow = WorkflowEvent.objects.get(workflow_name="DisbursementAdviceSent")
        WorkflowEvent.objects.filter(pk=workflow.pk).update(
            created_at=workflow.created_at + timedelta(seconds=1)
        )

        self.assertEqual(self._post().status_code, 409)

    def test_database_rejects_incomplete_stable_intent_delivery_truth(self):
        first = self._post()
        self.assertEqual(first.status_code, 200, first.content)
        counts = self._advice_counts()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.row.advice_intent.delivery_status = "pending"
                self.row.advice_intent.save(update_fields=["delivery_status"])

        replay = self._post()

        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(self._advice_counts(), counts)

    def test_replay_conflicts_for_each_recipient_rendered_and_provider_drift(self):
        first = self._post()
        self.assertEqual(first.status_code, 200, first.content)
        communication = Communication.objects.get(
            pk=first.json()["data"]["disbursement_advice_communication_id"]
        )
        cases = {
            "recipient_address": "changed.recipient@example.com",
            "subject_snapshot": "Changed subject snapshot",
            "body_snapshot": "Changed body snapshot",
            "content_template_id": None,
            "delivery_status": "delivered",
            "external_message_id": "manual:changed-provider-id",
            "sent_at": communication.sent_at + timedelta(seconds=1),
        }
        for field, changed in cases.items():
            with self.subTest(field=field):
                original = getattr(communication, field)
                Communication.objects.filter(pk=communication.pk).update(
                    **{field: changed}
                )
                self.assertEqual(self._post().status_code, 409)
                Communication.objects.filter(pk=communication.pk).update(
                    **{field: original}
                )

    def test_replay_uses_frozen_template_but_conflicts_on_ledger_drift(self):
        first = self._post()
        self.assertEqual(first.status_code, 200, first.content)
        template_cases = {
            "template_version": "2.0",
            "variables_json": [*ADVICE_VARIABLES, "unexpected"],
            "effective_to": timezone.localdate() - timedelta(days=1),
        }
        for field, changed in template_cases.items():
            with self.subTest(field=field):
                original = getattr(self.template, field)
                ContentTemplate.objects.filter(pk=self.template.pk).update(
                    **{field: changed}
                )
                self.assertEqual(self._post().status_code, 200)
                ContentTemplate.objects.filter(pk=self.template.pk).update(
                    **{field: original}
                )

        register = LoanRegisterUpdate.objects.get(disbursement=self.row)
        LoanRegisterUpdate.objects.filter(pk=register.pk).update(
            amount=register.amount + 1
        )
        self.assertEqual(self._post().status_code, 409)
        LoanRegisterUpdate.objects.filter(pk=register.pk).update(amount=register.amount)

        transfer = BankTransfer.objects.get(disbursement=self.row)
        BankTransfer.objects.filter(pk=transfer.pk).update(amount=transfer.amount + 1)
        self.assertEqual(self._post().status_code, 409)
        BankTransfer.objects.filter(pk=transfer.pk).update(amount=transfer.amount)

        workflow = WorkflowEvent.objects.get(workflow_name="DisbursementAdviceSent")
        WorkflowEvent.objects.filter(pk=workflow.pk).update(
            trigger_reason="changed retained workflow evidence"
        )
        self.assertEqual(self._post().status_code, 409)

    def test_validation_template_and_delivery_failures_create_no_advice_truth(self):
        unknown = self.client.post(
            f"/api/v1/disbursements/{self.row.pk}/send-advice/?force=true",
            {
                "channel": "email",
                "recipient_email": "borrower.advice@example.com",
                "message": "caller supplied text",
            },
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=f"advice-api:{self.row.pk}",
            **self.owner.owner.fixture._auth(self.actor),
        )
        wrong_channel = self.client.post(
            f"/api/v1/disbursements/{self.row.pk}/send-advice/",
            {
                "channel": "sms",
                "recipient_email": "borrower.advice@example.com",
            },
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=f"advice-api:{self.row.pk}",
            **self.owner.owner.fixture._auth(self.actor),
        )
        wrong_email = self._post(email="forged@example.com")
        self.assertEqual(unknown.status_code, 400, unknown.content)
        self.assertEqual(wrong_channel.status_code, 400, wrong_channel.content)
        self.assertEqual(wrong_email.status_code, 400, wrong_email.content)

        self.template.delete()
        missing_template = self._post()
        self.assertEqual(missing_template.status_code, 409, missing_template.content)
        self.template = ContentTemplate.objects.create(
            template_code="disbursement_advice_email_v1",
            template_name="Disbursement advice email",
            template_type="email",
            audience="borrower",
            subject_template="Advice {{borrower_name}}",
            body_template="Incomplete {{borrower_name}}",
            variables_json=ADVICE_VARIABLES,
            approval_status=ContentTemplate.STATUS_APPROVED,
            template_version="1.0",
            effective_from=timezone.localdate(),
        )
        invalid_variables = self._post()
        self.assertEqual(invalid_variables.status_code, 409, invalid_variables.content)
        self.template.delete()
        self.setUp_template()
        ContentTemplate.objects.create(
            template_code="disbursement_advice_email_v2",
            template_name="Other current advice",
            template_type="email",
            audience="borrower",
            subject_template=self.template.subject_template,
            body_template=self.template.body_template,
            variables_json=ADVICE_VARIABLES,
            approval_status=ContentTemplate.STATUS_APPROVED,
            template_version="2.0",
            effective_from=timezone.localdate(),
        )
        ambiguous = self._post()
        self.assertEqual(ambiguous.status_code, 409, ambiguous.content)
        ContentTemplate.objects.exclude(pk=self.template.pk).delete()

        class RejectingAdapter:
            def send_email(self, payload, idempotency_key):
                raise ValueError("provider rejected")

        with patch(
            "sfpcl_credit.tests.test_disbursement_advice_api."
            "FakeEmailDeliveryAdapter",
            return_value=RejectingAdapter(),
        ):
            rejected = self._post()
        self.assertEqual(rejected.status_code, 409, rejected.content)
        self.assertEqual(rejected.json()["error"]["code"], "DELIVERY_FAILED")
        self._assert_no_advice_truth()

    def test_provider_rejection_and_malformed_results_leave_outbox_retryable(self):
        class RejectingAdapter:
            def send_email(self, payload, idempotency_key):
                raise ValueError("provider rejected")

        class MalformedAdapter:
            def send_email(self, payload, idempotency_key):
                return {"delivery_status": "sent"}

        for expected_rejections, adapter in enumerate(
            (RejectingAdapter(), MalformedAdapter()), start=1
        ):
            with self.subTest(adapter=adapter.__class__.__name__):
                with patch(
                    "sfpcl_credit.tests.test_disbursement_advice_api."
                    "FakeEmailDeliveryAdapter",
                    return_value=adapter,
                ):
                    response = self._post()
                self.assertEqual(response.status_code, 409, response.content)
                self.assertEqual(response.json()["error"]["code"], "DELIVERY_FAILED")
                outbox = CommunicationDeliveryOutbox.objects.get(
                    advice_intent=self.row.advice_intent.pk
                )
                self.assertEqual(outbox.delivery_status, "pending")
                self.assertIsNone(outbox.provider_external_message_id)
                self.assertEqual(
                    CommunicationProviderAttempt.objects.filter(
                        outbox=outbox, outcome="rejected"
                    ).count(),
                    expected_rejections,
                )
                self.assertFalse(
                    DisbursementAdviceDeliveryReceipt.objects.filter(
                        advice_intent=self.row.advice_intent.pk
                    ).exists()
                )
                self._assert_no_advice_truth()

        accepted = self._post()
        self.assertEqual(accepted.status_code, 200, accepted.content)
        outbox.refresh_from_db()
        self.assertEqual(outbox.delivery_status, "sent")
        self.assertEqual(outbox.provider_attempts.count(), 3)
        self.assertEqual(outbox.provider_attempts.filter(outcome="accepted").count(), 1)
        self.assertEqual(
            outbox.provider_external_message_id,
            DisbursementAdviceDeliveryReceipt.objects.get(
                advice_intent=self.row.advice_intent.pk
            ).external_message_id,
        )

    def test_terminal_advice_without_outbox_never_reinvokes_provider_or_rewrites_outbox(
        self,
    ):
        accepted_at = timezone.now()
        Communication.objects.create(
            communication_id=self.row.advice_intent.pk,
            related_entity_type="disbursement",
            related_entity_id=self.row.pk,
            recipient_party_type="borrower",
            recipient_party_id=self.row.member_id,
            recipient_address="borrower.advice@example.com",
            channel="email",
            content_template=ContentTemplate.objects.get(),
            subject_snapshot="Legacy protected advice",
            body_snapshot="Legacy protected advice body",
            sent_by_user=self.actor,
            sent_at=accepted_at,
            delivery_status="sent",
            external_message_id="manual:legacy-pre-outbox-advice",
        )
        self.row.advice_intent.delivery_status = "sent"
        self.row.advice_intent.delivery_action_id = timezone.now().strftime(
            "00000000-0000-4000-8000-%m%d%H%M%S00"
        )
        self.row.advice_intent.delivery_evidence_digest = "a" * 64
        self.row.advice_intent.delivery_audit = self.row.transfer_success_audit
        self.row.advice_intent.delivery_workflow_event = (
            self.row.transfer_success_workflow_event
        )
        self.row.advice_intent.save()
        self.row.disbursement_advice_communication_id = self.row.advice_intent.pk
        self.row.save(update_fields=["disbursement_advice_communication"])

        class CountingAdapter(FakeEmailDeliveryAdapter):
            calls = 0

            def send_email(self, payload, idempotency_key):
                self.calls += 1
                return super().send_email(payload, idempotency_key)

        adapter = CountingAdapter()
        with patch(
            "sfpcl_credit.tests.test_disbursement_advice_api."
            "FakeEmailDeliveryAdapter",
            return_value=adapter,
        ):
            replay = self._post()

        self.assertEqual(replay.status_code, 409, replay.content)
        self.assertEqual(
            (
                adapter.calls,
                CommunicationDeliveryOutbox.objects.filter(
                    advice_intent=self.row.advice_intent.pk
                ).count(),
            ),
            (0, 0),
        )

    def test_legacy_partial_attempt_cannot_be_upgraded_or_redispatched(self):
        accepted = self._post()
        self.assertEqual(accepted.status_code, 200, accepted.content)
        outbox = CommunicationDeliveryOutbox.objects.get(
            advice_intent=self.row.advice_intent.pk
        )
        attempt = outbox.accepted_provider_attempt
        attempt.adapter_kind = "legacy:retained-outbox"
        attempt.evidence_digest = CommunicationDispatcher._attempt_digest(
            {
                "outbox": outbox,
                "advice_intent_id": attempt.advice_intent_id,
                "communication_id": attempt.communication_id,
                "idempotency_key": attempt.idempotency_key,
                "payload_digest": attempt.payload_digest,
                "adapter_kind": attempt.adapter_kind,
                "outcome": attempt.outcome,
                "provider_external_message_id": attempt.provider_external_message_id,
                "provider_delivery_status": attempt.provider_delivery_status,
                "provider_accepted_at": attempt.provider_accepted_at,
                "attempted_at": attempt.attempted_at,
            }
        )
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE communication_provider_attempts "
                "SET adapter_kind = %s, evidence_digest = %s "
                "WHERE provider_attempt_id = %s",
                [attempt.adapter_kind, attempt.evidence_digest, attempt.pk.hex],
            )
            self.assertEqual(cursor.rowcount, 1)
        class CountingAdapter(FakeEmailDeliveryAdapter):
            calls = 0

            def send_email(self, payload, idempotency_key):
                self.calls += 1
                return super().send_email(payload, idempotency_key)

        adapter = CountingAdapter()
        with patch(
            "sfpcl_credit.tests.test_disbursement_advice_api."
            "FakeEmailDeliveryAdapter",
            return_value=adapter,
        ):
            replay = self._post()

        self.assertEqual(replay.status_code, 409, replay.content)
        self.assertEqual(adapter.calls, 0)
        self.assertEqual(
            CommunicationDeliveryOutbox.objects.filter(pk=outbox.pk).count(), 1
        )
        self.assertEqual(
            Communication.objects.filter(pk=outbox.communication_id).count(), 1
        )

    def test_changed_valid_provider_tuple_cannot_become_terminal_delivery_truth(
        self,
    ):
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
                _send_advice_through_process(
                    actor=self.actor,
                    disbursement_id=self.row.pk,
                    payload={
                        "channel": "email",
                        "recipient_email": "borrower.advice@example.com",
                    },
                    adapter=adapter,
                )

        outbox = CommunicationDeliveryOutbox.objects.get(
            advice_intent=self.row.advice_intent.pk
        )
        CommunicationDeliveryOutbox.objects.filter(pk=outbox.pk).update(
            provider_external_message_id=(
                "manual:00000000-0000-4000-8000-000000000001"
            ),
            provider_accepted_at=outbox.provider_accepted_at + timedelta(seconds=1),
        )

        with self.assertRaises(DisbursementAdviceConflict):
            _send_advice_through_process(
                actor=self.actor,
                disbursement_id=self.row.pk,
                payload={
                    "channel": "email",
                    "recipient_email": "borrower.advice@example.com",
                },
                adapter=adapter,
            )

    def test_provider_and_template_evidence_is_complete_sealed_and_protected(self):
        accepted = self._post()
        self.assertEqual(accepted.status_code, 200, accepted.content)
        outbox = CommunicationDeliveryOutbox.objects.get(
            advice_intent=self.row.advice_intent.pk
        )
        attempt = CommunicationProviderAttempt.objects.get(outbox=outbox)

        self.assertEqual(outbox.accepted_provider_attempt, attempt)
        self.assertEqual(
            {
                "template_name_snapshot": self.template.template_name,
                "template_type_snapshot": self.template.template_type,
                "template_language_code_snapshot": self.template.language_code,
                "template_audience_snapshot": self.template.audience,
                "template_approval_status_snapshot": self.template.approval_status,
                "template_effective_from_snapshot": self.template.effective_from,
                "template_effective_to_snapshot": self.template.effective_to,
                "template_variables_snapshot": sorted(
                    self.template.variables_json
                ),
                "subject_template_snapshot": self.template.subject_template,
                "body_template_snapshot": self.template.body_template,
            },
            {
                field: getattr(outbox, field)
                for field in (
                    "template_name_snapshot",
                    "template_type_snapshot",
                    "template_language_code_snapshot",
                    "template_audience_snapshot",
                    "template_approval_status_snapshot",
                    "template_effective_from_snapshot",
                    "template_effective_to_snapshot",
                    "template_variables_snapshot",
                    "subject_template_snapshot",
                    "body_template_snapshot",
                )
            },
        )
        self.assertEqual(attempt.advice_intent_id, self.row.advice_intent.pk)
        self.assertEqual(attempt.communication_id, outbox.communication_id)
        self.assertEqual(attempt.idempotency_key, outbox.idempotency_key)
        self.assertEqual(attempt.payload_digest, outbox.payload_digest)
        self.assertEqual(attempt.outcome, "accepted")
        self.assertEqual(len(attempt.evidence_digest), 64)
        with self.assertRaises(ProtectedError):
            outbox.delete()
        with self.assertRaises(TypeError):
            attempt.delete()
        with self.assertRaises(ProtectedError):
            DisbursementAdviceDeliveryReceipt.objects.get(
                pk=outbox.delivery_receipt_id
            ).delete()
        with self.assertRaises(ProtectedError):
            Communication.objects.get(pk=outbox.final_communication_id).delete()

    def test_provider_attempt_one_field_mutations_are_zero_write_conflicts(self):
        first = self._post()
        self.assertEqual(first.status_code, 200, first.content)
        outbox = CommunicationDeliveryOutbox.objects.get(
            advice_intent=self.row.advice_intent.pk
        )
        attempt = CommunicationProviderAttempt.objects.get(outbox=outbox)
        cases = {
            "advice_intent_id": uuid.uuid4(),
            "communication_id": uuid.uuid4(),
            "idempotency_key": "changed-provider-attempt-key",
            "payload_digest": "b" * 64,
            "adapter_kind": "changed.Adapter",
            "provider_external_message_id": "manual:changed-sealed-provider",
            "provider_accepted_at": attempt.provider_accepted_at
            + timedelta(seconds=1),
            "attempted_at": attempt.attempted_at + timedelta(seconds=1),
            "evidence_digest": "c" * 64,
        }
        for field, changed in cases.items():
            with self.subTest(field=field):
                original = getattr(attempt, field)
                models.QuerySet(
                    model=CommunicationProviderAttempt, using="default"
                ).filter(pk=attempt.pk).update(
                    **{field: changed}
                )
                replay = self._post()
                self.assertEqual(replay.status_code, 409, replay.content)
                models.QuerySet(
                    model=CommunicationProviderAttempt, using="default"
                ).filter(pk=attempt.pk).update(
                    **{field: original}
                )

    def test_outbox_provenance_one_field_mutations_are_zero_write_conflicts(self):
        first = self._post()
        self.assertEqual(first.status_code, 200, first.content)
        outbox = CommunicationDeliveryOutbox.objects.get(
            advice_intent=self.row.advice_intent.pk
        )
        cases = {
            "template_name_snapshot": "Changed retained template name",
            "template_type_snapshot": "sms",
            "template_language_code_snapshot": "mr",
            "template_audience_snapshot": "staff",
            "template_approval_status_snapshot": "draft",
            "template_effective_from_snapshot": timezone.localdate()
            + timedelta(days=1),
            "template_effective_to_snapshot": timezone.localdate(),
            "template_variables_snapshot": [*ADVICE_VARIABLES, "unexpected"],
            "subject_template_snapshot": "Changed retained source subject",
            "body_template_snapshot": "Changed retained source body",
        }
        for field, changed in cases.items():
            with self.subTest(field=field):
                original = getattr(outbox, field)
                CommunicationDeliveryOutbox.objects.filter(pk=outbox.pk).update(
                    **{field: changed}
                )
                replay = self._post()
                self.assertEqual(replay.status_code, 409, replay.content)
                CommunicationDeliveryOutbox.objects.filter(pk=outbox.pk).update(
                    **{field: original}
                )

    def test_failure_after_complete_local_chain_rolls_back_but_acceptance_survives(
        self,
    ):
        real_save = type(self.row.advice_intent).save

        def fail_after_local_chain(instance, *args, **kwargs):
            if instance.delivery_status == "sent":
                self.assertEqual(
                    Communication.objects.filter(pk=instance.pk).count(), 1
                )
                self.assertEqual(
                    AuditLog.objects.filter(action="disbursement.advice_sent").count(),
                    1,
                )
                self.assertEqual(
                    WorkflowEvent.objects.filter(
                        workflow_name="DisbursementAdviceSent"
                    ).count(),
                    1,
                )
                self.assertEqual(DisbursementAdviceDeliveryReceipt.objects.count(), 1)
                raise RuntimeError("forced immediately before owner commit")
            return real_save(instance, *args, **kwargs)

        with patch.object(type(self.row.advice_intent), "save", fail_after_local_chain):
            with self.assertRaisesRegex(RuntimeError, "before owner commit"):
                _send_advice_through_process(
                    actor=self.actor,
                    disbursement_id=self.row.pk,
                    payload={
                        "channel": "email",
                        "recipient_email": "borrower.advice@example.com",
                    },
                    adapter=FakeEmailDeliveryAdapter(),
                )

        self.assertFalse(
            Communication.objects.filter(pk=self.row.advice_intent.pk).exists()
        )
        self.assertEqual(
            AuditLog.objects.filter(action="disbursement.advice_sent").count(), 0
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="DisbursementAdviceSent"
            ).count(),
            0,
        )
        self.assertEqual(DisbursementAdviceDeliveryReceipt.objects.count(), 0)
        outbox = CommunicationDeliveryOutbox.objects.get(
            advice_intent=self.row.advice_intent.pk
        )
        self.assertEqual(outbox.delivery_status, "sent")
        self.assertEqual(
            CommunicationProviderAttempt.objects.filter(
                outbox=outbox, outcome="accepted"
            ).count(),
            1,
        )

    def test_future_adapter_final_dispatch_replays_without_second_transport_call(self):
        class CountingTransport(FakeEmailDeliveryAdapter):
            calls = 0

            def send_email(self, payload, idempotency_key):
                self.calls += 1
                return super().send_email(payload, idempotency_key)

        transport = CountingTransport()
        first = _send_advice_through_process(
            actor=self.actor,
            disbursement_id=self.row.pk,
            payload={
                "channel": "email",
                "recipient_email": "borrower.advice@example.com",
            },
            adapter=FutureEmailDeliveryAdapter(transport=transport),
        )
        replay = _send_advice_through_process(
            actor=self.actor,
            disbursement_id=self.row.pk,
            payload={
                "channel": "email",
                "recipient_email": "borrower.advice@example.com",
            },
            adapter=FutureEmailDeliveryAdapter(transport=transport),
        )

        self.assertEqual(replay, first)
        self.assertEqual(transport.calls, 1)

    def test_permission_scope_and_stale_transfer_fail_closed(self):
        wrong_role = self.owner.owner.fixture.fixture._user(
            "field_officer", "Advice Scope Outsider"
        )
        self.owner.owner.fixture.fixture._grant(
            wrong_role, "finance.disbursement.send_advice"
        )
        denied_scope = self._post(actor=wrong_role)
        self.assertEqual(denied_scope.status_code, 403, denied_scope.content)
        self.assertEqual(
            denied_scope.json()["error"]["code"], "OBJECT_ACCESS_DENIED"
        )

        headers = self.owner.owner.fixture._auth(self.actor)
        self.actor.status = "inactive"
        self.actor.save(update_fields=["status"])
        inactive = self.client.post(
            f"/api/v1/disbursements/{self.row.pk}/send-advice/",
            {
                "channel": "email",
                "recipient_email": "borrower.advice@example.com",
            },
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=f"advice-api:{self.row.pk}",
            **headers,
        )
        self.assertEqual(inactive.status_code, 401, inactive.content)
        self.actor.status = "active"
        self.actor.save(update_fields=["status"])

        RolePermission.objects.filter(
            role=self.actor.primary_role,
            permission__permission_code="finance.disbursement.send_advice",
        ).delete()
        denied_grant = self._post()
        self.assertEqual(denied_grant.status_code, 403, denied_grant.content)
        self.owner.owner.fixture.fixture._grant(
            self.actor, "finance.disbursement.send_advice"
        )
        Permission.objects.filter(
            permission_code="finance.disbursement.send_advice"
        ).update(risk_level=Permission.RISK_HIGH)

        BankTransfer.objects.filter(disbursement=self.row).update(
            amount=self.row.disbursement_amount + 1
        )
        stale_transfer = self._post()
        self.assertEqual(stale_transfer.status_code, 409, stale_transfer.content)
        BankTransfer.objects.filter(disbursement=self.row).update(
            amount=self.row.disbursement_amount
        )

        LoanAccount.objects.filter(pk=self.row.loan_account_id).update(
            principal_outstanding=self.row.disbursement_amount + 1
        )
        stale = self._post()
        self.assertEqual(stale.status_code, 409, stale.content)
        self._assert_no_advice_truth()

    def setUp_template(self):
        self.template = ContentTemplate.objects.create(
            template_code="disbursement_advice_email_v1",
            template_name="Disbursement advice email",
            template_type="email",
            language_code="en",
            audience="borrower",
            subject_template=(
                "Disbursement advice {{application_reference_number}} / "
                "{{loan_account_number}}"
            ),
            body_template=(
                "Dear {{borrower_name}}, application {{application_reference_number}} "
                "and loan {{loan_account_number}} were sanctioned for "
                "{{sanctioned_amount}}. We transferred {{disbursement_amount}} on "
                "{{disbursed_at}} under reference {{bank_reference_number}}."
            ),
            variables_json=ADVICE_VARIABLES,
            approval_status=ContentTemplate.STATUS_APPROVED,
            template_version="1.0",
            effective_from=timezone.localdate(),
        )

    def _assert_no_advice_truth(self):
        self.row.refresh_from_db()
        self.assertIsNone(self.row.disbursement_advice_communication_id)
        self.row.advice_intent.refresh_from_db()
        self.assertEqual(self.row.advice_intent.delivery_status, "pending")
        self.assertFalse(
            Communication.objects.filter(
                related_entity_type="disbursement", related_entity_id=self.row.pk
            ).exists()
        )

        self.assertFalse(
            AuditLog.objects.filter(action="disbursement.advice_sent").exists()
        )
        self.assertFalse(
            WorkflowEvent.objects.filter(
                workflow_name="DisbursementAdviceSent"
            ).exists()
        )

    def _advice_counts(self):
        return (
            Communication.objects.filter(
                related_entity_type="disbursement", related_entity_id=self.row.pk
            ).count(),
            AuditLog.objects.filter(
                action="disbursement.advice_sent", entity_id=self.row.pk
            ).count(),
            WorkflowEvent.objects.filter(
                workflow_name="DisbursementAdviceSent", entity_id=self.row.pk
            ).count(),
        )

    def _post(self, *, email="borrower.advice@example.com", actor=None):
        response = self.client.post(
            f"/api/v1/disbursements/{self.row.pk}/send-advice/",
            {"channel": "email", "recipient_email": email},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-advice-001",
            HTTP_IDEMPOTENCY_KEY=f"advice-api:{self.row.pk}",
            **self.owner.owner.fixture._auth(actor or self.actor),
        )
        if response.status_code == 200 and response.json()["data"].get(
            "delivery_status"
        ) in {"queued", "retrying"}:
            from sfpcl_credit.processes.disbursement_advice_delivery import (
                execute_disbursement_advice_job,
            )

            job_id = response.json()["data"]["communication_job_id"]
            CommunicationDeliveryJob.objects.filter(pk=job_id).update(
                next_attempt_at=timezone.now()
            )
            result = execute_disbursement_advice_job(
                job_id, adapter=FakeEmailDeliveryAdapter()
            )
            if result["delivery_status"] in {"retrying", "failed"}:
                failed = JsonResponse(
                    {
                        "success": False,
                        "error": {"code": "DELIVERY_FAILED"},
                    },
                    status=409,
                )
                failed.json = lambda: {
                    "success": False,
                    "error": {"code": "DELIVERY_FAILED"},
                }
                return failed
            response = self.client.post(
                f"/api/v1/disbursements/{self.row.pk}/send-advice/",
                {"channel": "email", "recipient_email": email},
                content_type="application/json",
                HTTP_X_REQUEST_ID="req-advice-001",
                HTTP_IDEMPOTENCY_KEY=f"advice-api:{self.row.pk}",
                **self.owner.owner.fixture._auth(actor or self.actor),
            )
        return response


class PendingDisbursementAdviceApiTests(TestCase):
    def setUp(self):
        self.pending = transfer_fixtures.DisbursementAuthorisationApiTests(
            "test_cfc_approval_is_terminal_evidence_but_not_bank_execution"
        )
        self.pending.setUp()
        approved = self.pending._post(
            "approved", "Approved but not yet transferred for advice test."
        )
        self.assertEqual(approved.status_code, 200, approved.content)
        self.pending.fixture.fixture._grant(
            self.pending.fixture.actor, "finance.disbursement.send_advice"
        )
        Permission.objects.filter(
            permission_code="finance.disbursement.send_advice"
        ).update(risk_level=Permission.RISK_HIGH)
        self.pending.fixture.application.member.email = "pending.borrower@example.com"
        self.pending.fixture.application.member.save(update_fields=["email"])
        DisbursementAdviceApiTests.setUp_template(self)
        self.client = Client()

    def test_pending_transfer_cannot_send_advice(self):
        response = self.client.post(
            f"/api/v1/disbursements/{self.pending.disbursement_id}/send-advice/",
            {
                "channel": "email",
                "recipient_email": "pending.borrower@example.com",
            },
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=f"advice-api:{self.pending.disbursement_id}",
            **self.pending.fixture._auth(self.pending.fixture.actor),
        )

        self.assertEqual(response.status_code, 409, response.content)
        self.assertIsNone(
            Disbursement.objects.get(
                pk=self.pending.disbursement_id
            ).disbursement_advice_communication_id
        )


@skipUnless(connection.vendor == "postgresql", "PostgreSQL five-race acceptance")
class DisbursementAdviceRaceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = DisbursementAdviceApiTests(
            "test_public_success_sends_exact_advice_without_financial_side_effects"
        )
        fixture.setUp()
        self.actor_id = fixture.actor.pk
        self.disbursement_id = fixture.row.pk
        self.recipient_email = "borrower.advice@example.com"

    def test_five_advice_attempts_retain_one_accepted_delivery_run_one(self):
        self._run_five()

    def test_five_advice_attempts_retain_one_accepted_delivery_run_two(self):
        self._run_five()

    def _run_five(self):
        gate = Barrier(5)

        class CountingAdapter(FakeEmailDeliveryAdapter):
            calls = 0
            results = []

            def send_email(self, payload, idempotency_key):
                self.calls += 1
                result = super().send_email(payload, idempotency_key)
                self.results.append(result)
                return result

        adapter = CountingAdapter()

        def contender(_index):
            close_old_connections()
            try:
                actor = User.objects.get(pk=self.actor_id)
                gate.wait(timeout=15)
                try:
                    result = _send_advice_through_process(
                        actor=actor,
                        disbursement_id=self.disbursement_id,
                        payload={
                            "channel": "email",
                            "recipient_email": self.recipient_email,
                        },
                        adapter=adapter,
                    )
                    return ("winner", result["disbursement_advice_communication_id"])
                except DisbursementAdviceConflict as exc:
                    return ("clean_loser", str(exc))
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(contender, range(5)))

        winners = [value for outcome, value in results if outcome == "winner"]
        losers = [value for outcome, value in results if outcome == "clean_loser"]
        print(
            "advice_race_results=",
            results,
            "adapter_results=",
            len(adapter.results),
            "provider_identities=",
            len({result.external_message_id for result in adapter.results}),
        )
        self.assertEqual(len(winners), 1, results)
        self.assertEqual(len(losers), 4, results)
        self.assertGreaterEqual(adapter.calls, 1)
        self.assertEqual(len(adapter.results), adapter.calls)
        self.assertEqual(
            len({result.external_message_id for result in adapter.results}), 1
        )
        self.assertEqual(
            DisbursementAdviceDeliveryReceipt.objects.filter(
                advice_intent=winners[0]
            ).count(),
            1,
        )
        row = Disbursement.objects.get(pk=self.disbursement_id)
        intent = row.advice_intent
        self.assertEqual(str(row.disbursement_advice_communication_id), winners[0])
        self.assertEqual(intent.delivery_status, "sent")
        self.assertIsNotNone(intent.delivery_action_id)
        self.assertIsNotNone(intent.delivery_audit_id)
        self.assertIsNotNone(intent.delivery_workflow_event_id)
        self.assertTrue(intent.delivery_evidence_digest)
        self.assertEqual(CommunicationDeliveryOutbox.objects.count(), 1)
        outbox = CommunicationDeliveryOutbox.objects.get()
        self.assertEqual(
            CommunicationProviderAttempt.objects.filter(
                outbox=outbox, outcome="accepted"
            ).count(),
            1,
        )
        self.assertEqual(
            outbox.accepted_provider_attempt_id,
            outbox.provider_attempts.get().pk,
        )
        self.assertIsNotNone(outbox.delivery_receipt_id)
        self.assertIsNotNone(outbox.final_communication_id)
        self.assertEqual(
            Communication.objects.filter(
                related_entity_type="disbursement",
                related_entity_id=self.disbursement_id,
            ).count(),
            1,
        )
        self.assertEqual(
            AuditLog.objects.filter(action="disbursement.advice_sent").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="DisbursementAdviceSent"
            ).count(),
            1,
        )
