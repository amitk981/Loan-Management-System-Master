import hashlib
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from types import SimpleNamespace
from unittest.mock import patch

from django.db import close_old_connections, connection, connections
from django.test import Client, TestCase, TransactionTestCase
from unittest import skipUnless

from sfpcl_credit.tests.api_contracts import assert_success_envelope


class DisbursementAuthorisationApiTests(TestCase):
    password = "LoanAccountPass123!"

    def setUp(self):
        from sfpcl_credit.tests.test_final_documentation_approval_api import (
            FinalDocumentationApprovalApiTests,
        )

        owner = FinalDocumentationApprovalApiTests(
            "test_disbursement_readiness_real_owners_reach_a126_then_all_pass"
        )
        owner.setUp()
        facts = owner._real_owner_initiation_fixture(stop_before_initiation=True)
        payload = dict(facts["payload"])
        if self._testMethodName == "test_cfc_approves_exact_frozen_lesser_amount":
            payload["disbursement_amount"] = "250000.00"
        client = Client()
        initiated = client.post(
            f"/api/v1/loan-accounts/{facts['account'].pk}/disbursements/initiate/",
            payload,
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=f"cfc-initiation-{id(self)}",
            HTTP_X_REQUEST_ID="req-initiation-for-cfc",
            **owner.fixture._auth(facts["actor"]),
        )
        self.assertEqual(initiated.status_code, 200, initiated.content)
        from sfpcl_credit.identity.models import User

        def user_on_role(role, full_name):
            user = User.objects.create(
                full_name=full_name,
                email=f"{full_name.lower().replace(' ', '.')}@sfpcl.example",
                status="active",
                primary_role=role,
            )
            user.set_password(self.password)
            user.save()
            return user

        self.fixture = SimpleNamespace(
            fixture=SimpleNamespace(
                _user=owner.fixture._user,
                _user_on_role=user_on_role,
                _grant=owner._grant,
            ),
            actor=facts["actor"],
            application=owner.application,
            _auth=owner.fixture._auth,
            _user_on_role=user_on_role,
        )
        self.disbursement_id = initiated.json()["data"]["disbursement_id"]
        self.cfc = owner.fixture._user(
            "chief_financial_controller", "CFC Authoriser"
        )
        owner._grant(self.cfc, "finance.disbursement.authorise")
        self.cfc.approval_authority_type = "chief_financial_controller"
        self.cfc.save(update_fields=["approval_authority_type"])
        self.client = Client()

    def test_cfc_approves_exact_frozen_lesser_amount(self):
        from sfpcl_credit.disbursements.models import Disbursement

        response = self._post(
            "approved", "The lesser instruction amount is independently approved."
        )

        self.assertEqual(response.status_code, 200, response.content)
        row = Disbursement.objects.get(pk=self.disbursement_id)
        self.assertEqual(str(row.disbursement_amount), "250000.00")
        self.assertEqual(row.authorisation_status, "approved")
        self.assertEqual(
            row.authorisation_audit.new_value_json["disbursement_amount"],
            "250000.00",
        )

    def test_cfc_approval_is_terminal_evidence_but_not_bank_execution(self):
        from sfpcl_credit.communications.models import Communication, Notification
        from sfpcl_credit.disbursements.models import Disbursement
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import LoanAccount
        from sfpcl_credit.workflows.models import WorkflowEvent

        row = Disbursement.objects.get(pk=self.disbursement_id)
        account_before = LoanAccount.objects.values().get(pk=row.loan_account_id)
        communications_before = Communication.objects.count()

        response = self._post("approved", "  Beneficiary and instruction verified.  ")

        self.assertEqual(response.status_code, 200, response.content)
        assert_success_envelope(self, response.json())
        self.assertEqual(
            set(response.json()["data"]),
            {
                "disbursement_id",
                "authorisation_status",
                "bank_transfer_status",
                "authorised_at",
                "next_action",
            },
        )
        self.assertEqual(
            response.json()["data"]["disbursement_id"], self.disbursement_id
        )
        self.assertEqual(response.json()["data"]["authorisation_status"], "approved")
        self.assertEqual(response.json()["data"]["bank_transfer_status"], "pending")
        self.assertEqual(response.json()["data"]["next_action"], "record_bank_transfer")

        row.refresh_from_db()
        self.assertEqual(row.authorised_by_user_id, self.cfc.pk)
        self.assertEqual(row.authorisation_status, "approved")
        self.assertEqual(row.bank_transfer_status, "pending")
        self.assertEqual(
            row.authorisation_comments, "Beneficiary and instruction verified."
        )
        self.assertEqual(row.checker_role_code, "chief_financial_controller")
        self.assertTrue(row.authorised_at)
        self.assertTrue(row.authorisation_action_id)
        self.assertEqual(
            row.authorisation_evidence_digest,
            hashlib.sha256(
                row.initiation_audit.new_value_json["request_id"].encode()
                + row.readiness_digest.encode()
                + row.initiation_audit.new_value_json[
                    "final_verification_comment_digest"
                ].encode()
            ).hexdigest(),
        )
        self.assertIsNone(row.bank_reference_number)
        self.assertIsNone(row.disbursed_at)
        self.assertIsNone(row.disbursement_advice_communication_id)
        self.assertFalse(row.loan_register_updated_flag)
        self.assertEqual(
            LoanAccount.objects.values().get(pk=row.loan_account_id), account_before
        )
        self.assertEqual(Communication.objects.count(), communications_before)

        task = Notification.objects.get(pk=row.cfc_task_id)
        self.assertEqual(task.read_by_user_id, self.cfc.pk)
        self.assertEqual(task.read_at, row.authorised_at)
        self.assertEqual(task.action_label, "Approved")
        self.assertEqual(task.action_url, "")
        self.assertTrue(task.message.endswith("Decision: approved."))
        audit = AuditLog.objects.get(pk=row.authorisation_audit_id)
        self.assertEqual(audit.action, "disbursement.authorised")
        self.assertEqual(audit.new_value_json["outcome"], "approved")
        self.assertNotIn("comments", audit.new_value_json)
        self.assertEqual(
            audit.new_value_json["comments_digest"],
            hashlib.sha256(b"Beneficiary and instruction verified.").hexdigest(),
        )
        workflow = WorkflowEvent.objects.get(pk=row.authorisation_workflow_event_id)
        self.assertEqual(workflow.workflow_name, "DisbursementAuthorisation")
        self.assertEqual(workflow.from_state, "pending")
        self.assertEqual(workflow.to_state, "approved")

    def test_replaced_source_bank_governance_conflicts_without_decision_writes(self):
        from sfpcl_credit.disbursements.models import Disbursement
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.workflows.models import WorkflowEvent

        response = self._post(
            "approved", "Beneficiary and instruction verified.", source=None
        )

        self.assertEqual(response.status_code, 409, response.content)
        row = Disbursement.objects.get(pk=self.disbursement_id)
        self.assertEqual(row.authorisation_status, "pending")
        self.assertIsNone(row.authorised_by_user_id)
        self.assertFalse(
            AuditLog.objects.filter(action="disbursement.authorised").exists()
        )
        self.assertFalse(
            WorkflowEvent.objects.filter(
                workflow_name="DisbursementAuthorisation"
            ).exists()
        )
        self.assertIsNone(row.cfc_task.read_at)

    def test_rejection_closes_task_without_transfer_or_account_side_effects(self):
        from sfpcl_credit.communications.models import Communication
        from sfpcl_credit.disbursements.models import Disbursement
        from sfpcl_credit.loans.models import LoanAccount

        row = Disbursement.objects.get(pk=self.disbursement_id)
        account_before = LoanAccount.objects.values().get(pk=row.loan_account_id)
        communication_count = Communication.objects.count()
        response = self._post("rejected", "Beneficiary evidence requires correction.")

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["data"]["authorisation_status"], "rejected")
        self.assertEqual(response.json()["data"]["bank_transfer_status"], "pending")
        self.assertEqual(response.json()["data"]["next_action"], "none")
        row.refresh_from_db()
        self.assertEqual(row.authorisation_audit.action, "disbursement.rejected")
        self.assertEqual(row.authorisation_workflow_event.to_state, "rejected")
        self.assertEqual(row.cfc_task.read_by_user_id, self.cfc.pk)
        self.assertEqual(row.cfc_task.action_label, "Rejected")
        self.assertTrue(row.cfc_task.message.endswith("Decision: rejected."))
        self.assertIsNone(row.bank_reference_number)
        self.assertIsNone(row.disbursed_at)
        self.assertFalse(row.loan_register_updated_flag)
        self.assertEqual(
            LoanAccount.objects.values().get(pk=row.loan_account_id), account_before
        )
        self.assertEqual(Communication.objects.count(), communication_count)

    def test_exact_terminal_replay_is_zero_write_and_changed_replay_conflicts(self):
        from sfpcl_credit.disbursements.models import Disbursement
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.workflows.models import WorkflowEvent

        first = self._post("approved", "Beneficiary and instruction verified.")
        self.assertEqual(first.status_code, 200, first.content)
        row = Disbursement.objects.get(pk=self.disbursement_id)
        counts = (
            AuditLog.objects.filter(action="disbursement.authorised").count(),
            WorkflowEvent.objects.filter(
                workflow_name="DisbursementAuthorisation"
            ).count(),
            row.cfc_task.read_state_version,
        )
        replay = self._post("approved", "  Beneficiary and instruction verified.  ")
        changed = self._post("approved", "Different comments.")
        opposite = self._post("rejected", "Beneficiary and instruction verified.")

        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], first.json()["data"])
        self.assertEqual(changed.status_code, 409, changed.content)
        self.assertEqual(opposite.status_code, 409, opposite.content)
        row.refresh_from_db()
        self.assertEqual(
            (
                AuditLog.objects.filter(action="disbursement.authorised").count(),
                WorkflowEvent.objects.filter(
                    workflow_name="DisbursementAuthorisation"
                ).count(),
                row.cfc_task.read_state_version,
            ),
            counts,
        )

    def test_terminal_replay_fails_closed_when_retained_decision_evidence_changed(self):
        from sfpcl_credit.disbursements.models import Disbursement
        from sfpcl_credit.identity.models import AuditLog

        first = self._post("approved", "Beneficiary and instruction verified.")
        self.assertEqual(first.status_code, 200, first.content)
        row = Disbursement.objects.get()
        retained = dict(row.authorisation_audit.new_value_json)
        AuditLog.objects.filter(pk=row.authorisation_audit_id).update(
            new_value_json={**retained, "readiness_digest": "0" * 64}
        )

        replay = self._post("approved", "Beneficiary and instruction verified.")

        self.assertEqual(replay.status_code, 409, replay.content)
        self.assertEqual(replay.json()["error"]["code"], "CONFLICT")
        self.assertEqual(
            AuditLog.objects.filter(action="disbursement.authorised").count(), 1
        )

    def test_payload_permission_governance_and_maker_checker_fail_closed(self):
        from sfpcl_credit.disbursements.models import Disbursement
        from sfpcl_credit.identity.models import RolePermission

        malformed_cases = (
            ({"decision": "approve", "comments": "Valid comment."}, 400),
            ({"decision": "approved", "comments": "   "}, 400),
            ({"decision": "approved", "comments": "x" * 2001}, 400),
            ({"decision": "approved", "comments": "Valid.", "amount": "1"}, 400),
        )
        for payload, expected in malformed_cases:
            with self.subTest(payload=set(payload)):
                response = self.client.post(
                    f"/api/v1/disbursements/{self.disbursement_id}/authorise/",
                    payload,
                    content_type="application/json",
                    **self.fixture._auth(self.cfc),
                )
                self.assertEqual(response.status_code, expected, response.content)
        query = self._post("approved", "Valid comment.", query="?page=1")
        self.assertEqual(query.status_code, 400, query.content)

        wrong_role = self.fixture.fixture._user("field_officer", "Wrong CFC Role")
        self.fixture.fixture._grant(wrong_role, "finance.disbursement.authorise")
        denied = self._post("approved", "Valid comment.", actor=wrong_role)
        self.assertEqual(denied.status_code, 403, denied.content)

        RolePermission.objects.filter(
            role=self.cfc.primary_role,
            permission__permission_code="finance.disbursement.authorise",
        ).delete()
        denied = self._post("approved", "Valid comment.")
        self.assertEqual(denied.status_code, 403, denied.content)
        self.fixture.fixture._grant(self.cfc, "finance.disbursement.authorise")

        self.fixture.actor.approval_authority_type = "chief_financial_controller"
        self.fixture.actor.save(update_fields=["approval_authority_type"])
        self.fixture.fixture._grant(
            self.fixture.actor, "finance.disbursement.authorise"
        )
        maker_denied = self._post(
            "approved", "Valid comment.", actor=self.fixture.actor
        )
        self.assertEqual(maker_denied.status_code, 403, maker_denied.content)
        self.assertEqual(Disbursement.objects.get().authorisation_status, "pending")

    def test_governed_cfc_authority_on_non_finance_primary_role_can_act(self):
        from sfpcl_credit.disbursements.models import Disbursement

        governed = self.fixture.fixture._user("field_officer", "Governed CFC")
        governed.approval_authority_type = "chief_financial_controller"
        governed.save(update_fields=["approval_authority_type"])
        self.fixture.fixture._grant(governed, "finance.disbursement.authorise")

        response = self._post(
            "approved", "Independent governed review.", actor=governed
        )

        self.assertEqual(response.status_code, 200, response.content)
        row = Disbursement.objects.get()
        self.assertEqual(row.authorised_by_user_id, governed.pk)
        self.assertEqual(row.checker_role_code, "chief_financial_controller")

    def test_missing_disbursement_and_invalid_governed_authority_are_nondisclosing(
        self,
    ):
        from uuid import uuid4

        invalid = self.fixture.fixture._user("field_officer", "Invalid Authority")
        invalid.approval_authority_type = "invented_finance_authority"
        invalid.save(update_fields=["approval_authority_type"])
        self.fixture.fixture._grant(invalid, "finance.disbursement.authorise")
        denied = self._post("approved", "Independent review.", actor=invalid)
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(denied.json()["error"]["code"], "FORBIDDEN")

        missing = self.client.post(
            f"/api/v1/disbursements/{uuid4()}/authorise/",
            {"decision": "approved", "comments": "Independent review."},
            content_type="application/json",
            **self.fixture._auth(self.cfc),
        )
        self.assertEqual(missing.status_code, 403, missing.content)
        self.assertEqual(missing.json()["error"]["code"], "OBJECT_ACCESS_DENIED")

    def test_changed_initiation_task_and_readiness_ledgers_conflict_without_writes(
        self,
    ):
        from sfpcl_credit.disbursements.models import Disbursement
        from sfpcl_credit.identity.models import AuditLog

        row = Disbursement.objects.get()
        cases = (
            (
                row.initiation_audit.__class__,
                row.initiation_audit_id,
                "new_value_json",
                {
                    **row.initiation_audit.new_value_json,
                    "request_id": "replaced-request",
                },
                row.initiation_audit.new_value_json,
            ),
            (
                row.cfc_task.__class__,
                row.cfc_task_id,
                "action_url",
                "/replaced/",
                row.cfc_task.action_url,
            ),
            (
                Disbursement,
                row.pk,
                "readiness_evidence_json",
                {
                    **row.readiness_evidence_json,
                    "source_bank_governance_id": "replaced-governance",
                },
                row.readiness_evidence_json,
            ),
        )
        for model, pk, field, changed, original in cases:
            with self.subTest(field=field):
                model.objects.filter(pk=pk).update(**{field: changed})
                response = self._post("approved", "Independent review.")
                self.assertEqual(response.status_code, 409, response.content)
                self.assertFalse(
                    AuditLog.objects.filter(action="disbursement.authorised").exists()
                )
                model.objects.filter(pk=pk).update(**{field: original})

    def test_changed_current_borrower_bank_decision_denies_scope_and_both_decisions(self):
        from sfpcl_credit.disbursements.models import Disbursement
        from sfpcl_credit.disbursements.modules.disbursement_scope import has_cfc_scope
        from sfpcl_credit.members.models import BankAccount

        row = Disbursement.objects.get()
        self.assertTrue(
            has_cfc_scope(actor_id=self.cfc.pk, loan_account_id=row.loan_account_id)
        )
        original_ifsc = row.borrower_bank_account.ifsc
        BankAccount.objects.filter(pk=row.borrower_bank_account_id).update(
            ifsc="RBLB0000999"
        )

        self.assertFalse(
            has_cfc_scope(actor_id=self.cfc.pk, loan_account_id=row.loan_account_id)
        )
        for decision in ("approved", "rejected"):
            with self.subTest(decision=decision):
                response = self._post(decision, "Independent current-bank review.")
                self.assertEqual(response.status_code, 409, response.content)
                row.refresh_from_db()
                self.assertEqual(row.authorisation_status, "pending")
                self.assertIsNone(row.authorisation_audit_id)
        BankAccount.objects.filter(pk=row.borrower_bank_account_id).update(
            ifsc=original_ifsc
        )

    def test_pending_row_with_later_transfer_truth_cannot_be_authorised_or_rejected(self):
        from django.db import IntegrityError, transaction
        from django.utils import timezone

        from sfpcl_credit.disbursements.models import Disbursement

        row = Disbursement.objects.get()
        forged_cases = (
            {"bank_reference_number": "UTR-FORGED"},
            {"disbursed_at": timezone.now()},
            {"loan_register_updated_flag": True},
            {"bank_transfer_status": "processing"},
        )
        for changed in forged_cases:
            with self.subTest(changed=tuple(changed)):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    Disbursement.objects.filter(pk=row.pk).update(**changed)

    def test_pending_and_terminal_authorisation_aggregate_constraints_are_complete(self):
        from django.db import IntegrityError, transaction

        from sfpcl_credit.disbursements.models import Disbursement

        row = Disbursement.objects.get()
        invalid_pending = (
            {"authorisation_comments": "orphan"},
            {"checker_role_code": "chief_financial_controller"},
            {"authorisation_request_id": "orphan-request"},
            {"authorisation_evidence_digest": "0" * 64},
        )
        for changed in invalid_pending:
            with self.subTest(changed=tuple(changed)):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    Disbursement.objects.filter(pk=row.pk).update(**changed)

    def _post(self, decision, comments, *, actor=None, query="", source="real"):
        if source == "real":
            return self.client.post(
                f"/api/v1/disbursements/{self.disbursement_id}/authorise/{query}",
                {"decision": decision, "comments": comments},
                content_type="application/json",
                HTTP_X_REQUEST_ID="req-cfc-decision-001",
                **self.fixture._auth(actor or self.cfc),
            )
        with patch(
            "sfpcl_credit.disbursements.modules.disbursement_authorisation."
            "resolve_current_disbursement_evidence",
            return_value=source,
        ):
            return self.client.post(
                f"/api/v1/disbursements/{self.disbursement_id}/authorise/{query}",
                {"decision": decision, "comments": comments},
                content_type="application/json",
                HTTP_X_REQUEST_ID="req-cfc-decision-001",
                **self.fixture._auth(actor or self.cfc),
            )


@skipUnless(connection.vendor == "postgresql", "PostgreSQL five-race acceptance")
class DisbursementAuthorisationRaceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        from sfpcl_credit.identity.models import Role

        fixture = DisbursementAuthorisationApiTests(
            "test_cfc_approval_is_terminal_evidence_but_not_bank_execution"
        )
        fixture.setUp()
        self.fixture = fixture
        self.disbursement_id = fixture.disbursement_id
        self.actors = []
        primary_role, _ = Role.objects.get_or_create(
            role_code="race_non_finance_primary",
            defaults={
                "role_name": "Race Non-finance Primary",
                "status": "active",
            },
        )
        for index in range(5):
            actor = fixture.fixture._user_on_role(primary_role, f"Race CFC {index}")
            actor.approval_authority_type = "chief_financial_controller"
            actor.save(update_fields=["approval_authority_type"])
            fixture.fixture.fixture._grant(actor, "finance.disbursement.authorise")
            self.actors.append(actor)

    def test_five_cfc_decisions_retain_one_complete_winner_run_one(self):
        self._run_five()

    def test_five_cfc_decisions_retain_one_complete_winner_run_two(self):
        self._run_five()

    def _run_five(self):
        from sfpcl_credit.disbursements.models import Disbursement
        from sfpcl_credit.disbursements.modules.disbursement_workflow import (
            DisbursementAuthorisationConflict,
            DisbursementWorkflow,
        )
        from sfpcl_credit.identity.models import AuditLog, User
        from sfpcl_credit.workflows.models import WorkflowEvent

        gate = Barrier(5)

        def contender(index):
            close_old_connections()
            try:
                actor = User.objects.get(pk=self.actors[index].pk)
                gate.wait(timeout=15)
                try:
                    result = DisbursementWorkflow.authorise(
                        actor=actor,
                        disbursement_id=self.disbursement_id,
                        payload={
                            "decision": "approved" if index % 2 == 0 else "rejected",
                            "comments": f"Independent race decision {index}.",
                        },
                    )
                    return ("won", result["authorisation_status"])
                except DisbursementAuthorisationConflict:
                    return ("conflict", None)
            finally:
                connections["default"].close()

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(contender, range(5)))

        self.assertEqual(len([result for result in results if result[0] == "won"]), 1)
        self.assertEqual(
            len([result for result in results if result[0] == "conflict"]), 4
        )
        row = Disbursement.objects.get(pk=self.disbursement_id)
        self.assertIn(row.authorisation_status, {"approved", "rejected"})
        self.assertEqual(row.bank_transfer_status, "pending")
        self.assertEqual(row.cfc_task.read_by_user_id, row.authorised_by_user_id)
        self.assertEqual(
            AuditLog.objects.filter(
                action__in=("disbursement.authorised", "disbursement.rejected")
            ).count(),
            1,
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="DisbursementAuthorisation"
            ).count(),
            1,
        )
