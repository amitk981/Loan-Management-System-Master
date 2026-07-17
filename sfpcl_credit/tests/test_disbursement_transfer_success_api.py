from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from unittest import skipUnless
from uuid import uuid4

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import (
    IntegrityError,
    close_old_connections,
    connection,
    connections,
    transaction,
)
from django.test import Client, RequestFactory, TestCase, TransactionTestCase
from django.utils import timezone

from sfpcl_credit.communications.models import Communication
from sfpcl_credit.disbursements.models import BankTransfer, Disbursement
from sfpcl_credit.disbursements.modules.disbursement_workflow import (
    DisbursementTransferConflict,
    DisbursementWorkflow,
)
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.documents.services import store_document_upload
from sfpcl_credit.identity.models import AuditLog, RolePermission, User
from sfpcl_credit.legal_documents.models import DocumentChecklist
from sfpcl_credit.loans.models import LoanAccount, LoanStatusHistory
from sfpcl_credit.tests.api_contracts import assert_success_envelope
from sfpcl_credit.tests.test_disbursement_authorisation_api import (
    DisbursementAuthorisationApiTests,
)
from sfpcl_credit.tracer.models import Repayment
from sfpcl_credit.workflows.models import WorkflowEvent


class DisbursementTransferSuccessApiTests(TestCase):
    def setUp(self):
        owner = DisbursementAuthorisationApiTests(
            "test_cfc_approval_is_terminal_evidence_but_not_bank_execution"
        )
        owner.setUp()
        approved = owner._post(
            "approved", "Beneficiary and instruction verified for transfer."
        )
        self.assertEqual(approved.status_code, 200, approved.content)
        owner.fixture.fixture._grant(owner.cfc, "finance.disbursement.mark_success")
        self.owner = owner
        self.actor = owner.cfc
        self.client = Client()
        self.evidence = store_document_upload(
            user=self.actor,
            request=RequestFactory().post(
                "/api/v1/documents/", REMOTE_ADDR="127.0.0.1"
            ),
            uploaded_file=SimpleUploadedFile(
                "rbl-transfer-evidence.pdf",
                b"%PDF-1.4 sanitized transfer evidence",
                content_type="application/pdf",
            ),
            document_category="finance",
            sensitivity_level="restricted",
            related_entity_type="loan_application",
            related_entity_id=owner.fixture.application.pk,
        )

    def test_public_success_records_transfer_and_activates_exact_loan_atomically(self):
        row = Disbursement.objects.get(pk=self.owner.disbursement_id)
        account = LoanAccount.objects.get(pk=row.loan_account_id)
        communication_count = Communication.objects.count()
        repayment_count = Repayment.objects.count()
        checklist_before = list(DocumentChecklist.objects.values())

        response = self._post(
            bank_reference_number="  RBL-UTR-0001  ",
            disbursed_at=timezone.now(),
        )

        self.assertEqual(response.status_code, 200, response.content)
        assert_success_envelope(self, response.json())
        self.assertEqual(
            response.json()["data"],
            {
                "disbursement_id": str(row.pk),
                "bank_transfer_status": "successful",
                "loan_account_status": "active",
                "disbursement_advice_communication_id": None,
            },
        )
        row.refresh_from_db()
        account.refresh_from_db()
        self.assertEqual(row.authorisation_status, "approved")
        self.assertEqual(row.bank_transfer_status, "successful")
        self.assertEqual(row.bank_reference_number, "RBL-UTR-0001")
        self.assertEqual(row.bank_transfer_evidence_document_id, self.evidence.pk)
        self.assertIsNone(row.disbursement_advice_communication_id)
        self.assertFalse(row.loan_register_updated_flag)
        self.assertEqual(account.loan_account_status, "active")
        self.assertEqual(account.disbursed_amount, row.disbursement_amount)
        self.assertEqual(account.principal_outstanding, row.disbursement_amount)
        self.assertEqual(account.total_outstanding, row.disbursement_amount)
        self.assertEqual(account.interest_outstanding, 0)
        self.assertEqual(account.charges_outstanding, 0)
        self.assertEqual(account.tenure_start_date, row.disbursed_at.date())

        transfer = BankTransfer.objects.get(disbursement=row)
        self.assertEqual(transfer.bank_reference_number_normalized, "RBL-UTR-0001")
        self.assertEqual(transfer.amount, row.disbursement_amount)
        self.assertEqual(transfer.loan_account_id, account.pk)
        self.assertEqual(transfer.source_bank_account_id, row.source_bank_account_id)
        self.assertEqual(
            transfer.destination_bank_account_id, row.borrower_bank_account_id
        )
        self.assertEqual(transfer.bank_status, "successful")
        self.assertEqual(transfer.payment_method, "manual")
        history = LoanStatusHistory.objects.get(
            loan_account=account, from_status="sanctioned", to_status="active"
        )
        self.assertEqual(history.changed_by_user_id, self.actor.pk)
        audit = AuditLog.objects.get(action="disbursement.transfer_succeeded")
        workflow = WorkflowEvent.objects.get(
            workflow_name="DisbursementTransferSucceeded"
        )
        self.assertEqual(audit.entity_id, row.pk)
        self.assertEqual(workflow.entity_id, row.pk)
        self.assertEqual(audit.new_value_json["bank_transfer_id"], str(transfer.pk))
        self.assertEqual(
            audit.new_value_json["loan_status_history_id"], str(history.pk)
        )
        self.assertNotIn("bank_reference_number", audit.new_value_json)
        self.assertIn("bank_reference_digest", audit.new_value_json)
        self.assertEqual(Communication.objects.count(), communication_count)
        self.assertEqual(Repayment.objects.count(), repayment_count)
        self.assertEqual(list(DocumentChecklist.objects.values()), checklist_before)

    def test_exact_retry_is_zero_write_and_changed_replays_conflict(self):
        accepted_at = timezone.now()
        first = self._post(
            bank_reference_number="RBL-REPLAY-0001", disbursed_at=accepted_at
        )
        self.assertEqual(first.status_code, 200, first.content)
        counts = (
            BankTransfer.objects.count(),
            LoanStatusHistory.objects.count(),
            AuditLog.objects.filter(action="disbursement.transfer_succeeded").count(),
            WorkflowEvent.objects.filter(
                workflow_name="DisbursementTransferSucceeded"
            ).count(),
        )

        replay = self._post(
            bank_reference_number="  rbl-replay-0001 ", disbursed_at=accepted_at
        )
        changed_payload = self._post(
            bank_reference_number="RBL-REPLAY-CHANGED",
            disbursed_at=accepted_at,
        )
        changed_key = self._post(
            bank_reference_number="RBL-REPLAY-0001",
            disbursed_at=accepted_at,
            key="different-transfer-key",
        )

        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], first.json()["data"])
        self.assertEqual(changed_payload.status_code, 409, changed_payload.content)
        self.assertEqual(changed_key.status_code, 409, changed_key.content)
        self.assertEqual(
            (
                BankTransfer.objects.count(),
                LoanStatusHistory.objects.count(),
                AuditLog.objects.filter(
                    action="disbursement.transfer_succeeded"
                ).count(),
                WorkflowEvent.objects.filter(
                    workflow_name="DisbursementTransferSucceeded"
                ).count(),
            ),
            counts,
        )
        self.assertEqual(
            Disbursement.objects.get().bank_reference_number, "RBL-REPLAY-0001"
        )

    def test_validation_permission_and_scope_fail_closed_without_transfer_writes(self):
        row = Disbursement.objects.get()
        account_before = LoanAccount.objects.values().get(pk=row.loan_account_id)
        history_count = LoanStatusHistory.objects.count()
        malformed = (
            (
                {
                    "bank_reference_number": "",
                    "disbursed_at": timezone.now(),
                    "evidence": self.evidence.pk,
                },
                400,
            ),
            (
                {
                    "bank_reference_number": "UTR-X",
                    "disbursed_at": row.authorised_at - timedelta(seconds=1),
                    "evidence": self.evidence.pk,
                },
                400,
            ),
            (
                {
                    "bank_reference_number": "UTR-X",
                    "disbursed_at": timezone.now() + timedelta(minutes=6),
                    "evidence": self.evidence.pk,
                },
                400,
            ),
            (
                {
                    "bank_reference_number": "UTR-X",
                    "disbursed_at": timezone.now(),
                    "evidence": uuid4(),
                },
                400,
            ),
        )
        for payload, expected in malformed:
            with self.subTest(
                reference=payload["bank_reference_number"], evidence=payload["evidence"]
            ):
                response = self._post(
                    bank_reference_number=payload["bank_reference_number"],
                    disbursed_at=payload["disbursed_at"],
                    evidence_id=payload["evidence"],
                )
                self.assertEqual(response.status_code, expected, response.content)

        no_key = self._post(
            bank_reference_number="UTR-NO-KEY",
            disbursed_at=timezone.now(),
            key="",
        )
        query = self._post(
            bank_reference_number="UTR-QUERY",
            disbursed_at=timezone.now(),
            query="?status=successful",
        )
        self.assertEqual(no_key.status_code, 400, no_key.content)
        self.assertEqual(query.status_code, 400, query.content)

        wrong_role = self.owner.fixture.fixture._user(
            "field_officer", "Transfer Scope Outsider"
        )
        self.owner.fixture.fixture._grant(
            wrong_role, "finance.disbursement.mark_success"
        )
        denied = self._post(
            bank_reference_number="UTR-DENIED",
            disbursed_at=timezone.now(),
            actor=wrong_role,
        )
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(denied.json()["error"]["code"], "OBJECT_ACCESS_DENIED")

        headers = self.owner.fixture._auth(self.actor)
        self.actor.status = "inactive"
        self.actor.save(update_fields=["status"])
        inactive = self.client.post(
            f"/api/v1/disbursements/{row.pk}/mark-transfer-successful/",
            {
                "bank_reference_number": "UTR-INACTIVE",
                "disbursed_at": timezone.now().isoformat().replace("+00:00", "Z"),
                "bank_transfer_evidence_document_id": str(self.evidence.pk),
            },
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="inactive-transfer-actor",
            **headers,
        )
        self.assertEqual(inactive.status_code, 401, inactive.content)
        self.actor.status = "active"
        self.actor.save(update_fields=["status"])

        RolePermission.objects.filter(
            role=self.actor.primary_role,
            permission__permission_code="finance.disbursement.mark_success",
        ).delete()
        denied = self._post(
            bank_reference_number="UTR-NO-GRANT", disbursed_at=timezone.now()
        )
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(denied.json()["error"]["code"], "FORBIDDEN")

        self.assertEqual(BankTransfer.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="disbursement.transfer_succeeded").count(),
            0,
        )
        self.assertEqual(LoanStatusHistory.objects.count(), history_count)
        self.assertEqual(
            LoanAccount.objects.values().get(pk=row.loan_account_id), account_before
        )

    def test_changed_authorisation_and_upload_evidence_conflict_without_success(self):
        row = Disbursement.objects.get()
        history_count = LoanStatusHistory.objects.count()
        account_before = LoanAccount.objects.values().get(pk=row.loan_account_id)
        retained = dict(row.authorisation_audit.new_value_json)
        AuditLog.objects.filter(pk=row.authorisation_audit_id).update(
            new_value_json={**retained, "authorisation_evidence_digest": "0" * 64}
        )
        stale_authorisation = self._post(
            bank_reference_number="UTR-STALE-AUTH", disbursed_at=timezone.now()
        )
        self.assertEqual(
            stale_authorisation.status_code, 409, stale_authorisation.content
        )
        AuditLog.objects.filter(pk=row.authorisation_audit_id).update(
            new_value_json=retained
        )

        DocumentFile.objects.filter(pk=self.evidence.pk).update(
            checksum_sha256="0" * 64
        )
        stale_upload = self._post(
            bank_reference_number="UTR-STALE-FILE", disbursed_at=timezone.now()
        )
        self.assertEqual(stale_upload.status_code, 400, stale_upload.content)
        cross_object = store_document_upload(
            user=self.actor,
            request=RequestFactory().post(
                "/api/v1/documents/", REMOTE_ADDR="127.0.0.1"
            ),
            uploaded_file=SimpleUploadedFile(
                "cross-object.pdf", b"%PDF cross object", "application/pdf"
            ),
            document_category="finance",
            sensitivity_level="restricted",
            related_entity_type="loan_application",
            related_entity_id=uuid4(),
        )
        cross_response = self._post(
            bank_reference_number="UTR-CROSS-FILE",
            disbursed_at=timezone.now(),
            evidence_id=cross_object.pk,
        )
        self.assertEqual(cross_response.status_code, 400, cross_response.content)
        self.assertEqual(BankTransfer.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="disbursement.transfer_succeeded").count(),
            0,
        )
        self.assertEqual(LoanStatusHistory.objects.count(), history_count)
        self.assertEqual(
            LoanAccount.objects.values().get(pk=row.loan_account_id), account_before
        )

    def test_exact_retry_fails_closed_when_retained_success_ledger_changes(self):
        accepted_at = timezone.now()
        first = self._post(
            bank_reference_number="RBL-LEDGER-0001", disbursed_at=accepted_at
        )
        self.assertEqual(first.status_code, 200, first.content)
        row = Disbursement.objects.get()
        retained = dict(row.transfer_success_audit.new_value_json)
        AuditLog.objects.filter(pk=row.transfer_success_audit_id).update(
            new_value_json={**retained, "bank_reference_digest": "0" * 64}
        )

        replay = self._post(
            bank_reference_number="RBL-LEDGER-0001", disbursed_at=accepted_at
        )

        self.assertEqual(replay.status_code, 409, replay.content)
        self.assertEqual(replay.json()["error"]["code"], "CONFLICT")
        self.assertEqual(BankTransfer.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="disbursement.transfer_succeeded").count(),
            1,
        )
        AuditLog.objects.filter(pk=row.transfer_success_audit_id).update(
            new_value_json=retained
        )
        authorisation = dict(row.authorisation_audit.new_value_json)
        AuditLog.objects.filter(pk=row.authorisation_audit_id).update(
            new_value_json={**authorisation, "comments_digest": "0" * 64}
        )
        stale_authorisation = self._post(
            bank_reference_number="RBL-LEDGER-0001", disbursed_at=accepted_at
        )
        self.assertEqual(
            stale_authorisation.status_code, 409, stale_authorisation.content
        )

    def test_operational_senior_finance_initiator_can_record_approved_transfer(self):
        maker = self.owner.fixture.actor
        self.owner.fixture.fixture._grant(maker, "finance.disbursement.mark_success")
        response = self._post(
            bank_reference_number="X1",
            disbursed_at=timezone.now(),
            actor=maker,
        )

        self.assertEqual(response.status_code, 200, response.content)
        row = Disbursement.objects.get()
        self.assertEqual(row.transfer_success_actor_user_id, maker.pk)
        self.assertEqual(row.transfer_success_role_code, "senior_manager_finance")
        self.assertEqual(
            row.transfer_success_audit.new_value_json["bank_reference_masked"], "**"
        )

    def test_database_rejects_partial_success_and_over_sanction_funding(self):
        row = Disbursement.objects.get()
        self.assertTrue(
            BankTransfer._meta.get_field("bank_reference_number_normalized").unique
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            Disbursement.objects.filter(pk=row.pk).update(
                bank_transfer_evidence_document=self.evidence
            )
        with self.assertRaises(IntegrityError), transaction.atomic():
            LoanAccount.objects.filter(pk=row.loan_account_id).update(
                disbursed_amount=row.loan_account.sanctioned_amount + 1
            )

        accepted = self._post(
            bank_reference_number="RBL-DB-0001", disbursed_at=timezone.now()
        )
        self.assertEqual(accepted.status_code, 200, accepted.content)
        row.refresh_from_db()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Disbursement.objects.filter(pk=row.pk).update(
                transfer_success_action_id=None
            )

    def test_rejected_instruction_and_forged_outcome_fields_are_zero_write(self):
        row = Disbursement.objects.get()
        Disbursement.objects.filter(pk=row.pk).update(authorisation_status="rejected")
        rejected = self._post(
            bank_reference_number="RBL-REJECTED-0001", disbursed_at=timezone.now()
        )
        self.assertEqual(rejected.status_code, 409, rejected.content)

        forged = self.client.post(
            f"/api/v1/disbursements/{row.pk}/mark-transfer-successful/",
            {
                "bank_reference_number": "RBL-FORGED-0001",
                "disbursed_at": timezone.now().isoformat().replace("+00:00", "Z"),
                "bank_transfer_evidence_document_id": str(self.evidence.pk),
                "bank_transfer_status": "successful",
                "loan_account_status": "active",
            },
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="forged-outcome",
            **self.owner.fixture._auth(self.actor),
        )
        malformed_json = self.client.post(
            f"/api/v1/disbursements/{row.pk}/mark-transfer-successful/",
            data=b'{"bank_reference_number":',
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="malformed-json",
            **self.owner.fixture._auth(self.actor),
        )
        self.assertEqual(forged.status_code, 400, forged.content)
        self.assertEqual(malformed_json.status_code, 400, malformed_json.content)
        self.assertEqual(BankTransfer.objects.count(), 0)
        self.assertEqual(
            AuditLog.objects.filter(action="disbursement.transfer_succeeded").count(),
            0,
        )

    def test_already_active_or_partially_funded_account_conflicts_without_success(self):
        row = Disbursement.objects.get()
        account = row.loan_account
        history_count = LoanStatusHistory.objects.count()
        drift_cases = (
            {"loan_account_status": "active"},
            {
                "loan_account_status": "sanctioned",
                "disbursed_amount": 1,
                "principal_outstanding": 1,
                "total_outstanding": 1,
            },
        )
        for changed in drift_cases:
            with self.subTest(changed=tuple(changed)):
                LoanAccount.objects.filter(pk=account.pk).update(**changed)
                response = self._post(
                    bank_reference_number="RBL-DRIFT-0001",
                    disbursed_at=timezone.now(),
                )
                self.assertEqual(response.status_code, 409, response.content)
                LoanAccount.objects.filter(pk=account.pk).update(
                    loan_account_status="sanctioned",
                    disbursed_amount=0,
                    principal_outstanding=0,
                    total_outstanding=0,
                )
        self.assertEqual(BankTransfer.objects.count(), 0)
        self.assertEqual(LoanStatusHistory.objects.count(), history_count)
        self.assertEqual(
            AuditLog.objects.filter(action="disbursement.transfer_succeeded").count(),
            0,
        )

    def _post(
        self,
        *,
        bank_reference_number,
        disbursed_at,
        key="transfer-success-1",
        evidence_id=None,
        actor=None,
        query="",
    ):
        return self.client.post(
            f"/api/v1/disbursements/{self.owner.disbursement_id}/mark-transfer-successful/{query}",
            {
                "bank_reference_number": bank_reference_number,
                "disbursed_at": disbursed_at.isoformat().replace("+00:00", "Z"),
                "bank_transfer_evidence_document_id": str(
                    evidence_id or self.evidence.pk
                ),
            },
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=key,
            HTTP_X_REQUEST_ID="req-transfer-success-001",
            **self.owner.fixture._auth(actor or self.actor),
        )


@skipUnless(connection.vendor == "postgresql", "PostgreSQL five-race acceptance")
class DisbursementTransferSuccessRaceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        fixture = DisbursementAuthorisationApiTests(
            "test_cfc_approval_is_terminal_evidence_but_not_bank_execution"
        )
        fixture.setUp()
        approved = fixture._post(
            "approved", "Beneficiary and instruction verified for transfer race."
        )
        self.assertEqual(approved.status_code, 200, approved.content)
        fixture.fixture.fixture._grant(fixture.cfc, "finance.disbursement.mark_success")
        self.actor_id = fixture.cfc.pk
        self.disbursement_id = fixture.disbursement_id
        self.evidence = store_document_upload(
            user=fixture.cfc,
            request=RequestFactory().post(
                "/api/v1/documents/", REMOTE_ADDR="127.0.0.1"
            ),
            uploaded_file=SimpleUploadedFile(
                "race-transfer-evidence.pdf",
                b"%PDF-1.4 sanitized race evidence",
                content_type="application/pdf",
            ),
            document_category="finance",
            sensitivity_level="restricted",
            related_entity_type="loan_application",
            related_entity_id=fixture.fixture.application.pk,
        )

    def test_five_transfer_attempts_retain_one_complete_winner_run_one(self):
        self._run_five()

    def test_five_transfer_attempts_retain_one_complete_winner_run_two(self):
        self._run_five()

    def _run_five(self):
        gate = Barrier(5)
        accepted_at = timezone.now().isoformat().replace("+00:00", "Z")

        def contender(index):
            close_old_connections()
            try:
                actor = User.objects.get(pk=self.actor_id)
                gate.wait(timeout=15)
                try:
                    result = DisbursementWorkflow.mark_transfer_successful(
                        actor=actor,
                        disbursement_id=self.disbursement_id,
                        payload={
                            "bank_reference_number": f"RBL-RACE-{index:04d}",
                            "disbursed_at": accepted_at,
                            "bank_transfer_evidence_document_id": str(self.evidence.pk),
                        },
                        idempotency_key=f"transfer-race-{index}",
                    )
                    return ("won", result["disbursement_id"])
                except DisbursementTransferConflict:
                    return ("conflict", None)
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(contender, range(5)))

        self.assertEqual(len([item for item in results if item[0] == "won"]), 1)
        self.assertEqual(len([item for item in results if item[0] == "conflict"]), 4)
        row = Disbursement.objects.get(pk=self.disbursement_id)
        account = LoanAccount.objects.get(pk=row.loan_account_id)
        transfer = BankTransfer.objects.get(disbursement=row)
        self.assertEqual(row.bank_transfer_status, "successful")
        self.assertEqual(account.loan_account_status, "active")
        self.assertEqual(account.disbursed_amount, row.disbursement_amount)
        self.assertEqual(transfer.amount, row.disbursement_amount)
        self.assertEqual(
            LoanStatusHistory.objects.filter(
                loan_account=account, from_status="sanctioned", to_status="active"
            ).count(),
            1,
        )
        self.assertEqual(
            AuditLog.objects.filter(action="disbursement.transfer_succeeded").count(),
            1,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="DisbursementTransferSucceeded"
            ).count(),
            1,
        )
