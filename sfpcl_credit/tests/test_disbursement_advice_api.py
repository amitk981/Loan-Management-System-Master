from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless
from unittest.mock import patch

from django.db import close_old_connections, connection, connections
from django.test import Client, TestCase, TransactionTestCase
from django.utils import timezone

from sfpcl_credit.communications.adapters import FakeEmailDeliveryAdapter
from sfpcl_credit.communications.models import Communication, ContentTemplate
from sfpcl_credit.disbursements.models import BankTransfer, Disbursement
from sfpcl_credit.disbursements.modules.disbursement_workflow import (
    DisbursementWorkflow,
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
        owner.owner.fixture.fixture._grant(
            owner.actor, "finance.disbursement.send_advice"
        )
        Permission.objects.filter(
            permission_code="finance.disbursement.send_advice"
        ).update(risk_level=Permission.RISK_HIGH)
        self.owner = owner
        self.actor = owner.actor
        self.client = Client()
        self.row = Disbursement.objects.select_related(
            "member", "loan_application", "loan_account"
        ).get(pk=owner.owner.disbursement_id)
        self.row.member.email = "Borrower.Advice@Example.com"
        self.row.member.save(update_fields=["email"])
        self.setUp_template()

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
        self.assertEqual(
            LoanAccount.objects.values().get(pk=self.row.loan_account_id),
            account_before,
        )
        self.assertEqual(list(DocumentChecklist.objects.values()), checklist_before)
        self.assertEqual(Repayment.objects.count(), repayment_count)
        self.assertFalse(self.row.loan_register_updated_flag)

    def test_exact_replay_is_zero_write_and_changed_replay_conflicts(self):
        class CountingAdapter(FakeEmailDeliveryAdapter):
            calls = 0

            def send_email(self, payload, idempotency_key):
                self.calls += 1
                return super().send_email(payload, idempotency_key)

        adapter = CountingAdapter()
        with patch(
            "sfpcl_credit.disbursements.modules.disbursement_advice."
            "ManualEmailDeliveryAdapter",
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

    def test_validation_template_and_delivery_failures_create_no_advice_truth(self):
        unknown = self.client.post(
            f"/api/v1/disbursements/{self.row.pk}/send-advice/?force=true",
            {
                "channel": "email",
                "recipient_email": "borrower.advice@example.com",
                "message": "caller supplied text",
            },
            content_type="application/json",
            **self.owner.owner.fixture._auth(self.actor),
        )
        wrong_channel = self.client.post(
            f"/api/v1/disbursements/{self.row.pk}/send-advice/",
            {
                "channel": "sms",
                "recipient_email": "borrower.advice@example.com",
            },
            content_type="application/json",
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
            "sfpcl_credit.disbursements.modules.disbursement_advice."
            "ManualEmailDeliveryAdapter",
            return_value=RejectingAdapter(),
        ):
            rejected = self._post()
        self.assertEqual(rejected.status_code, 409, rejected.content)
        self.assertEqual(rejected.json()["error"]["code"], "DELIVERY_FAILED")
        self._assert_no_advice_truth()

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

    def _post(self, *, email="borrower.advice@example.com", actor=None):
        return self.client.post(
            f"/api/v1/disbursements/{self.row.pk}/send-advice/",
            {"channel": "email", "recipient_email": email},
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-advice-001",
            **self.owner.owner.fixture._auth(actor or self.actor),
        )


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
            self.pending.cfc, "finance.disbursement.send_advice"
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
            **self.pending.fixture._auth(self.pending.cfc),
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

            def send_email(self, payload, idempotency_key):
                self.calls += 1
                return super().send_email(payload, idempotency_key)

        adapter = CountingAdapter()

        def contender(_index):
            close_old_connections()
            try:
                actor = User.objects.get(pk=self.actor_id)
                gate.wait(timeout=15)
                result = DisbursementWorkflow.send_advice(
                    actor=actor,
                    disbursement_id=self.disbursement_id,
                    payload={
                        "channel": "email",
                        "recipient_email": self.recipient_email,
                    },
                    adapter=adapter,
                )
                return result["disbursement_advice_communication_id"]
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(contender, range(5)))

        self.assertEqual(len(set(results)), 1)
        self.assertEqual(adapter.calls, 1)
        row = Disbursement.objects.get(pk=self.disbursement_id)
        self.assertEqual(str(row.disbursement_advice_communication_id), results[0])
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
