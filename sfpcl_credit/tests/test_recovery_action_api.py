import json
from django.test import Client, TestCase


class RecoveryActionApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_recovery_decision_api import (
            RecoveryDecisionApiTests,
        )

        fixture = RecoveryDecisionApiTests(
            "test_matching_terminal_approval_creates_one_frozen_decision"
        )
        fixture.setUp()
        self.fixture = fixture
        self.account = fixture.fixture.account
        self.client = Client()
    def _approved_decision(self, action="invoke_sh4"):
        created, case, approvers, _ = self.fixture._submitted_case(action)
        self.fixture._force_terminal_approval(case, approvers)
        response = self.client.post(
            f"/api/v1/default-cases/{created['default_case_id']}/recovery-decision/",
            data=json.dumps(self.fixture._decision_payload(case, action)),
            content_type="application/json",
            **self.fixture._grant_decider(approvers[0]),
        )
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()["data"], case
    def _executor(self):
        user_fixture = (
            self.fixture.fixture.fixture.fixture.fixture.fixture.fixture.fixture
            .owner.fixture.fixture
        )
        auth_fixture = (
            self.fixture.fixture.fixture.fixture.fixture.fixture.fixture.fixture
            .owner.fixture
        )
        actor = user_fixture._user("company_secretary", "Recovery Company Secretary")
        user_fixture._grant(
            actor,
            "defaults.case.read",
            "recovery.action.initiate",
            "recovery.action.complete",
        )
        return actor, auth_fixture._auth(actor)
    def _recovery_evidence(self, actor):
        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.legal_documents.models import LoanDocument

        document = DocumentFile.objects.create(
            file_name="recovery-invocation-evidence.pdf",
            storage_provider="local",
            storage_key="tests/recovery/invocation-evidence.pdf",
            checksum_sha256="e" * 64,
            sensitivity_level="restricted",
            uploaded_by_user=actor,
        )
        LoanDocument.objects.create(
            loan_application=self.account.loan_application,
            document_type="recovery_invocation_evidence",
            document_category="recovery",
            document=document,
            output_format="pdf",
            generation_status="generated",
            execution_status="pending",
            verification_status="pending",
        )
        return document
    def _held_sh4(self, actor):
        from sfpcl_credit.security_instruments.models import SH4ShareTransferForm

        form = SH4ShareTransferForm.objects.get(
            security_package__loan_application=self.account.loan_application
        )
        self.assertEqual(form.form_status, "held_in_custody")
        return form
    @staticmethod
    def _initiation_payload(evidence):
        return {
            "action_type": "invoke_sh4",
            "initiated_at": "2028-09-30T10:00:00Z",
            "evidence_document_ids": [str(evidence.pk)],
            "remarks": "SH-4 invocation initiated with borrower notice retained.",
            "interaction_log": [
                {
                    "interaction_at": "2028-09-29T09:30:00Z",
                    "interaction_mode": "borrower_contact",
                    "person_contacted": "Borrower",
                    "summary": "Approved recovery route explained without third-party disclosure.",
                    "next_action": "Company Secretary to initiate the approved SH-4 route.",
                    "complaint_raised": False,
                    "grievance_reference": "/grievances",
                    "evidence_document_ids": [str(evidence.pk)],
                }
            ],
        }
    def test_company_secretary_initiates_exact_approved_sh4_with_governed_evidence(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.recovery.models import RecoveryAction

        decision, approval_case = self._approved_decision()
        actor, auth = self._executor()
        form = self._held_sh4(actor)
        evidence = self._recovery_evidence(actor)

        response = self.client.post(
            f"/api/v1/recovery-decisions/{decision['recovery_decision_id']}/actions/",
            data=json.dumps(self._initiation_payload(evidence)),
            content_type="application/json",
            **auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        action = RecoveryAction.objects.get()
        self.assertEqual(data["recovery_action_id"], str(action.pk))
        self.assertEqual(data["action_status"], "pending")
        self.assertEqual(data["source_security"]["security_type"], "sh4")
        self.assertEqual(data["source_security"]["security_id"], str(form.pk))
        self.assertIsNone(form.__class__.objects.get(pk=form.pk).invocation_approval_case_id)
        self.assertEqual(action.approval_case_id, approval_case.pk)
        self.assertEqual(data["available_actions"][0]["action_code"], "complete_recovery")
        self.assertEqual(
            AuditLog.objects.filter(action="recovery.action.initiated").count(), 1
        )
    def test_completion_posts_one_atomic_recovery_ledger_movement_and_replays_exactly(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import LoanAccount
        from sfpcl_credit.recovery.models import RecoveryAction

        decision, _ = self._approved_decision()
        actor, auth = self._executor()
        self._held_sh4(actor)
        evidence = self._recovery_evidence(actor)
        initiated = self.client.post(
            f"/api/v1/recovery-decisions/{decision['recovery_decision_id']}/actions/",
            data=json.dumps(self._initiation_payload(evidence)),
            content_type="application/json",
            **auth,
        )
        self.assertEqual(initiated.status_code, 200, initiated.content)
        action_id = initiated.json()["data"]["recovery_action_id"]
        before = LoanAccount.objects.get(pk=self.account.pk)
        payload = {
            "completed_at": "2028-10-15T10:00:00Z",
            "amount_recovered": "1000.00",
            "evidence_document_ids": [str(evidence.pk)],
            "remarks": "Verified SH-4 proceeds received and posted to the loan ledger.",
        }
        first = self.client.post(
            f"/api/v1/recovery-actions/{action_id}/complete/",
            data=json.dumps(payload),
            content_type="application/json",
            **auth,
        )
        replay = self.client.post(
            f"/api/v1/recovery-actions/{action_id}/complete/",
            data=json.dumps(payload),
            content_type="application/json",
            **auth,
        )
        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(first.json()["data"], replay.json()["data"])
        action = RecoveryAction.objects.get(pk=action_id)
        after = LoanAccount.objects.get(pk=self.account.pk)
        self.assertEqual(action.action_status, "completed")
        self.assertEqual(action.amount_recovered, 1000)
        self.assertEqual(after.principal_outstanding, before.principal_outstanding - 1000)
        self.assertEqual(after.interest_outstanding, before.interest_outstanding)
        self.assertEqual(after.total_outstanding, before.total_outstanding - 1000)
        self.assertEqual(action.ledger_posting_json["credit_amount"], "1000.00")
        self.assertEqual(
            action.ledger_posting_json["principal_after"],
            f"{after.principal_outstanding:.2f}",
        )
        self.assertEqual(action.external_sap_status, "pending")
        self.assertEqual(
            AuditLog.objects.filter(action="recovery.proceeds_posted").count(), 1
        )
        self.assertEqual(
            AuditLog.objects.filter(action="recovery.action.completed").count(), 1
        )
