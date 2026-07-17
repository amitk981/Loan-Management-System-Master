import hashlib
import json
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from django.db import close_old_connections, connection, connections
from django.test import Client, TestCase, TransactionTestCase
from unittest import skipUnless

from sfpcl_credit.tests.api_contracts import assert_success_envelope


CHECK_CODES = [
    "sanction_approved",
    "loan_account_sanctioned",
    "exception_approval_complete",
    "general_meeting_approval_complete",
    "kyc_complete",
    "appraisal_complete",
    "documentation_complete",
    "company_secretary_approval",
    "credit_manager_approval",
    "sanction_committee_approval",
    "security_package_complete",
    "poa_complete",
    "term_sheet_complete",
    "loan_agreement_complete",
    "sh4_complete",
    "cdsl_pledge_complete",
    "blank_dated_cheque_received",
    "cancelled_cheque_verified",
    "bank_account_verified",
    "signature_mismatch_resolved",
    "sap_customer_code_present",
    "source_bank_account_configured",
    "amount_within_sanction",
]


class DisbursementInitiationApiTests(TestCase):
    password = "LoanAccountPass123!"

    def setUp(self):
        from sfpcl_credit.tests.test_loan_account_creation_api import (
            LoanAccountCreationApiTests,
        )

        fixture = LoanAccountCreationApiTests(
            "test_terminal_sanction_creates_unfunded_account_terms_and_evidence"
        )
        fixture.setUp()
        created = fixture._post(
            {
                "sanction_decision_id": str(fixture.sanction.pk),
                "loan_account_number": "LN-INITIATE-001",
            }
        )
        self.assertEqual(created.status_code, 200, created.content)
        self.fixture = fixture
        self.application = fixture.application
        self.account_id = created.json()["data"]["loan_account_id"]
        self.actor = fixture.actor
        self.actor.primary_role.role_code = "senior_manager_finance"
        self.actor.primary_role.save(update_fields=["role_code"])
        fixture._grant(self.actor, "finance.disbursement.initiate")
        self.cfc = fixture._user("chief_financial_controller", "CFC Authoriser")
        fixture._grant(self.cfc, "finance.disbursement.authorise")
        from sfpcl_credit.members.models import BankAccount

        borrower_bank = BankAccount.objects.create(
            owner_party_type="member",
            owner_party_id=self.application.member_id,
            account_holder_name="Test Member",
            account_number_encrypted="encrypted-borrower",
            account_number_hash="borrower-hash",
            account_number_last4="1001",
            ifsc="TEST0000001",
            bank_name="Test Bank",
            verification_status="verified",
            status="active",
        )
        source_bank = BankAccount.objects.create(
            owner_party_type="sfpcl",
            owner_party_id=uuid4(),
            account_holder_name="SFPCL",
            account_number_encrypted="encrypted-source",
            account_number_hash="source-hash",
            account_number_last4="2002",
            ifsc="RBLB0000001",
            bank_name="RBL Bank",
            verification_status="verified",
            status="active",
        )
        self.borrower_bank_id = borrower_bank.pk
        self.source_bank_id = source_bank.pk
        self.bank_decision_id = uuid4()
        self.sap_code_id = uuid4()
        self.sap_request_id = uuid4()
        self.client = Client()

    def test_current_ready_payment_is_recorded_once_without_transfer_side_effects(self):
        from sfpcl_credit.communications.models import Communication, Notification
        from sfpcl_credit.disbursements.models import Disbursement
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import LoanAccount
        from sfpcl_credit.workflows.models import WorkflowEvent

        account_before = LoanAccount.objects.values().get(pk=self.account_id)
        communications_before = Communication.objects.count()
        response = self._post()

        self.assertEqual(response.status_code, 200, response.content)
        assert_success_envelope(self, response.json())
        self.assertEqual(
            set(response.json()["data"]),
            {
                "disbursement_id",
                "initiation_status",
                "authorisation_status",
                "bank_transfer_status",
            },
        )
        self.assertEqual(
            response.json()["data"] | {"disbursement_id": "retained"},
            {
                "disbursement_id": "retained",
                "initiation_status": "initiated",
                "authorisation_status": "pending",
                "bank_transfer_status": "pending",
            },
        )
        row = Disbursement.objects.get(pk=response.json()["data"]["disbursement_id"])
        self.assertEqual(row.loan_account_id, account_before["loan_account_id"])
        self.assertEqual(row.loan_application_id, self.application.pk)
        self.assertEqual(row.member_id, self.application.member_id)
        self.assertEqual(str(row.disbursement_amount), "400000.00")
        self.assertEqual(row.borrower_bank_account_id, self.borrower_bank_id)
        self.assertEqual(row.source_bank_account_id, self.source_bank_id)
        self.assertEqual(row.initiated_by_user_id, self.actor.pk)
        self.assertEqual(row.final_verification_comments, "Final facts verified.")
        self.assertEqual(row.payment_method, "manual")
        self.assertEqual(row.maker_role_code, "senior_manager_finance")
        self.assertIsNone(row.authorised_by_user_id)
        self.assertIsNone(row.bank_reference_number)
        self.assertIsNone(row.disbursed_at)
        self.assertIsNone(row.disbursement_advice_communication_id)
        self.assertFalse(row.loan_register_updated_flag)
        self.assertEqual(row.readiness_digest, row.readiness_evidence_json["check_digest"])
        self.assertEqual(
            row.readiness_evidence_json["sap_profile_request_id"],
            str(self.sap_request_id),
        )
        self.assertEqual(LoanAccount.objects.values().get(pk=self.account_id), account_before)
        self.assertEqual(Communication.objects.count(), communications_before)
        task = Notification.objects.get(pk=row.cfc_task_id)
        self.assertIsNone(task.recipient_user_id)
        self.assertEqual(task.recipient_role_code, "chief_financial_controller")
        self.assertEqual(task.related_entity_id, row.pk)
        audit = AuditLog.objects.get(pk=row.initiation_audit_id)
        self.assertEqual(audit.action, "disbursement.initiated")
        self.assertEqual(audit.entity_id, row.pk)
        self.assertEqual(audit.new_value_json["outcome"], "initiated")
        workflow = WorkflowEvent.objects.get(pk=row.initiation_workflow_event_id)
        self.assertEqual(workflow.to_state, "initiated")
        self.assertEqual(workflow.triggered_by_user_id, self.actor.pk)
        self.assertEqual(
            Disbursement.objects.count(),
            AuditLog.objects.filter(action="disbursement.initiated").count(),
        )
        secret_surface = str(audit.new_value_json) + str(task.__dict__) + str(workflow.__dict__)
        for forbidden in ("encrypted-borrower", "encrypted-source", "borrower-hash", "source-hash"):
            self.assertNotIn(forbidden, secret_surface)
        self.assertEqual(self.readiness_mock.call_count, 1)
        self.readiness_mock.assert_called_once_with(
            actor=AuditLog.objects.get(pk=row.initiation_audit_id).actor_user,
            loan_account_id=row.loan_account_id,
        )

    def test_exact_replay_writes_nothing_and_changed_replay_or_duplicate_conflicts(self):
        from sfpcl_credit.communications.models import Notification
        from sfpcl_credit.disbursements.models import Disbursement
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.workflows.models import WorkflowEvent

        first = self._post()
        counts = (
            Disbursement.objects.count(),
            Notification.objects.count(),
            AuditLog.objects.filter(action="disbursement.initiated").count(),
            WorkflowEvent.objects.filter(workflow_name="DisbursementInitiated").count(),
        )
        replay = self._post()
        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(first.json()["data"], replay.json()["data"])
        changed_time_readiness = self._readiness()
        changed_time_readiness["evaluated_at"] = "2099-01-01T00:00:00Z"
        time_only_replay = self._post(readiness=changed_time_readiness)
        self.assertEqual(time_only_replay.status_code, 200, time_only_replay.content)
        self.assertEqual(first.json()["data"], time_only_replay.json()["data"])
        self.assertEqual(
            (
                Disbursement.objects.count(),
                Notification.objects.count(),
                AuditLog.objects.filter(action="disbursement.initiated").count(),
                WorkflowEvent.objects.filter(workflow_name="DisbursementInitiated").count(),
            ),
            counts,
        )

        changed = self._post(comments="Changed verification.")
        self.assertEqual(changed.status_code, 409, changed.content)
        self.assertEqual(changed.json()["error"]["code"], "DISBURSEMENT_CONFLICT")
        changed_evidence = self._readiness()
        changed_evidence["_evidence"]["sap_profile_request_id"] = str(uuid4())
        stale_replay = self._post(readiness=changed_evidence)
        self.assertEqual(stale_replay.status_code, 409, stale_replay.content)
        duplicate = self._post(key="initiation-002")
        self.assertEqual(duplicate.status_code, 409, duplicate.content)
        self.assertEqual(Disbursement.objects.count(), 1)

    def test_strict_payload_header_amount_and_bank_contracts_are_zero_write(self):
        from sfpcl_credit.disbursements.models import Disbursement

        cases = [
            ({"unexpected": "value"}, "initiation-001", 400),
            ({"disbursement_amount": "0"}, "initiation-001", 400),
            ({"disbursement_amount": "400000.001"}, "initiation-001", 400),
            ({"disbursement_amount": "10000000000000000"}, "initiation-001", 400),
            ({"final_verification_comments": ["not", "text"]}, "initiation-001", 400),
            ({"disbursement_amount": "400000.01"}, "initiation-001", 409),
            ({"borrower_bank_account_id": str(uuid4())}, "initiation-001", 409),
            ({"source_bank_account_id": str(uuid4())}, "initiation-001", 409),
            ({}, None, 400),
        ]
        for changes, key, expected in cases:
            with self.subTest(changes=changes, key=key):
                response = self._post(changes=changes, key=key)
                self.assertEqual(response.status_code, expected, response.content)
                self.assertEqual(Disbursement.objects.count(), 0)
        unknown_query = self.client.post(
            f"/api/v1/loan-accounts/{self.account_id}/disbursements/initiate/?page=1",
            {},
            content_type="application/json",
            **self._auth(),
        )
        self.assertEqual(unknown_query.status_code, 400, unknown_query.content)
        malformed = self.client.post(
            f"/api/v1/loan-accounts/{self.account_id}/disbursements/initiate/",
            "{",
            content_type="application/json",
            **self._auth(),
        )
        self.assertEqual(malformed.status_code, 400, malformed.content)
        self.assertEqual(Disbursement.objects.count(), 0)

    def test_role_grant_scope_cfc_and_exact_readiness_contracts_fail_closed(self):
        from sfpcl_credit.disbursements.models import Disbursement
        from sfpcl_credit.identity.models import RolePermission

        wrong_role = self.fixture._user("field_officer", "Wrong Role")
        self.fixture._grant(wrong_role, "finance.disbursement.initiate")
        denied = self._post(actor=wrong_role)
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(denied.json()["error"]["code"], "FORBIDDEN")
        RolePermission.objects.filter(
            role=self.actor.primary_role,
            permission__permission_code="finance.disbursement.initiate",
        ).delete()
        denied = self._post(actor=self.actor)
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(denied.json()["error"]["code"], "FORBIDDEN")
        self.fixture._grant(self.actor, "finance.disbursement.initiate")
        self.assertEqual(Disbursement.objects.count(), 0)

        variants = []
        failed = self._readiness()
        failed["checks"][0]["status"] = "fail"
        failed["ready_for_disbursement"] = False
        variants.append(failed)
        reordered = self._readiness()
        reordered["checks"][0], reordered["checks"][1] = (
            reordered["checks"][1],
            reordered["checks"][0],
        )
        variants.append(reordered)
        extra = self._readiness()
        extra["checks"].append({"code": "forged", "label": "forged", "status": "pass"})
        variants.append(extra)
        changed_digest = self._readiness()
        changed_digest["_evidence"]["check_digest"] = "0" * 64
        variants.append(changed_digest)
        missing_sap = self._readiness()
        missing_sap["_evidence"]["sap_profile_request_id"] = None
        variants.append(missing_sap)
        for readiness in variants:
            with self.subTest(checks=len(readiness["checks"])):
                response = self._post(readiness=readiness)
                self.assertEqual(response.status_code, 409, response.content)
                self.assertEqual(response.json()["error"]["code"], "DISBURSEMENT_NOT_READY")
                self.assertEqual(Disbursement.objects.count(), 0)

    def test_cfc_readiness_scope_exists_only_after_exact_assigned_initiation(self):
        self.fixture._grant(self.cfc, "finance.disbursement.readiness")
        before = self.client.get(
            f"/api/v1/loan-accounts/{self.account_id}/disbursement-readiness/",
            **self._auth(self.cfc),
        )
        self.assertEqual(before.status_code, 403, before.content)
        self.assertEqual(before.json()["error"]["code"], "OBJECT_ACCESS_DENIED")

        initiated = self._post()
        self.assertEqual(initiated.status_code, 200, initiated.content)
        after = self.client.get(
            f"/api/v1/loan-accounts/{self.account_id}/disbursement-readiness/",
            **self._auth(self.cfc),
        )
        self.assertEqual(after.status_code, 200, after.content)

    def test_inaccessible_or_changed_account_and_source_configuration_are_zero_write(self):
        from sfpcl_credit.configurations.modules.configuration_resolver import (
            resolve_source_bank_account,
        )
        from sfpcl_credit.disbursements.models import Disbursement
        from sfpcl_credit.loans.models import LoanAccount
        from sfpcl_credit.members.models import BankAccount

        source = resolve_source_bank_account()
        self.assertEqual(source.source_bank_account_id, self.source_bank_id)
        self.assertFalse(hasattr(source, "account_number_encrypted"))
        BankAccount.objects.create(
            owner_party_type="sfpcl",
            owner_party_id=uuid4(),
            account_holder_name="SFPCL duplicate",
            account_number_encrypted="encrypted-duplicate",
            account_number_hash="source-hash-duplicate",
            account_number_last4="3003",
            ifsc="RBLB0000002",
            bank_name="RBL Bank",
            verification_status="verified",
            status="active",
        )
        self.assertIsNone(resolve_source_bank_account())
        BankAccount.objects.filter(account_number_hash="source-hash-duplicate").update(
            status="inactive"
        )

        LoanAccount.objects.filter(pk=self.account_id).update(
            loan_account_status="active"
        )
        changed = self._post()
        self.assertEqual(changed.status_code, 409, changed.content)
        self.assertEqual(Disbursement.objects.count(), 0)

        missing_id = uuid4()
        readiness = self._readiness()
        readiness["loan_account_id"] = str(missing_id)
        response = self._post_for_account(missing_id, readiness)
        self.assertEqual(response.status_code, 403, response.content)
        self.assertEqual(response.json()["error"]["code"], "OBJECT_ACCESS_DENIED")
        self.assertEqual(Disbursement.objects.count(), 0)

    def _readiness(self):
        checks = [
            {"code": code, "label": code.replace("_", " "), "status": "pass"}
            for code in CHECK_CODES
        ]
        canonical = [{"code": item["code"], "status": item["status"]} for item in checks]
        return {
            "loan_account_id": self.account_id,
            "loan_application_id": str(self.application.pk),
            "ready_for_disbursement": True,
            "evaluated_at": "2026-07-17T07:30:00Z",
            "checks": checks,
            "_evidence": {
                "check_digest": hashlib.sha256(
                    json.dumps(canonical, separators=(",", ":")).encode()
                ).hexdigest(),
                "sap_customer_code_id": str(self.sap_code_id),
                "sap_profile_request_id": str(self.sap_request_id),
                "borrower_bank_account_id": str(self.borrower_bank_id),
                "bank_verification_decision_id": str(self.bank_decision_id),
                "source_bank_account_id": str(self.source_bank_id),
            },
        }

    def _post(
        self,
        *,
        changes=None,
        comments="  Final facts verified.  ",
        key="initiation-001",
        actor=None,
        readiness=None,
    ):
        payload = {
            "disbursement_amount": "400000.00",
            "borrower_bank_account_id": str(self.borrower_bank_id),
            "source_bank_account_id": str(self.source_bank_id),
            "final_verification_comments": comments,
        }
        payload.update(changes or {})
        bank = SimpleNamespace(
            valid=True,
            member_id=self.application.member_id,
            bank_account_id=self.borrower_bank_id,
            cancelled_cheque_id=uuid4(),
            bank_verification_decision_id=self.bank_decision_id,
            audit_log_id=uuid4(),
            workflow_event_id=uuid4(),
            version_history_id=uuid4(),
        )
        source = SimpleNamespace(
            source_bank_account_id=self.source_bank_id,
            active=True,
            bank_name="RBL Bank",
        )
        with (
            patch(
                "sfpcl_credit.disbursements.modules.disbursement_readiness."
                "DisbursementReadinessModule.evaluate",
                return_value=deepcopy(readiness or self._readiness()),
            ) as readiness_mock,
            patch(
                "sfpcl_credit.applications.modules.document_checklist_facts."
                "resolve_blank_cheque_bank_fact",
                return_value=bank,
            ),
            patch(
                "sfpcl_credit.configurations.modules.configuration_resolver."
                "resolve_source_bank_account",
                return_value=source,
            ),
        ):
            response = self.client.post(
                f"/api/v1/loan-accounts/{self.account_id}/disbursements/initiate/",
                payload,
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY=key,
                **self._auth(actor or self.actor),
            )
        self.readiness_mock = readiness_mock
        return response

    def _post_for_account(self, account_id, readiness):
        with patch(
            "sfpcl_credit.disbursements.modules.disbursement_readiness."
            "DisbursementReadinessModule.evaluate",
            return_value=readiness,
        ):
            return self.client.post(
                f"/api/v1/loan-accounts/{account_id}/disbursements/initiate/",
                {
                    "disbursement_amount": "400000.00",
                    "borrower_bank_account_id": str(self.borrower_bank_id),
                    "source_bank_account_id": str(self.source_bank_id),
                    "final_verification_comments": "Final facts verified.",
                },
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="missing-account",
                **self._auth(),
            )

    def _auth(self, actor=None):
        actor = actor or self.actor
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": actor.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {
            "HTTP_AUTHORIZATION": f"Bearer {response.json()['data']['access_token']}"
        }

    def _user_on_role(self, role, full_name):
        from sfpcl_credit.identity.models import User

        user = User.objects.create(
            full_name=full_name,
            email=f"{full_name.lower().replace(' ', '.')}@sfpcl.example",
            status="active",
            primary_role=role,
        )
        user.set_password(self.password)
        user.save()
        return user


@skipUnless(connection.vendor == "postgresql", "PostgreSQL five-race acceptance")
class DisbursementInitiationRaceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.fixture = DisbursementInitiationApiTests(
            "test_current_ready_payment_is_recorded_once_without_transfer_side_effects"
        )
        self.fixture.setUp()

    def test_five_changed_initiations_retain_one_complete_winner_run_one(self):
        self._run_five()

    def test_five_changed_initiations_retain_one_complete_winner_run_two(self):
        self._run_five()

    def _run_five(self):
        from sfpcl_credit.disbursements.models import Disbursement
        from sfpcl_credit.disbursements.modules.disbursement_initiation import (
            DisbursementConflict,
            initiate,
        )
        from sfpcl_credit.identity.models import AuditLog, User
        from sfpcl_credit.communications.models import Notification
        from sfpcl_credit.workflows.models import WorkflowEvent

        bank = SimpleNamespace(
            valid=True,
            member_id=self.fixture.application.member_id,
            bank_account_id=self.fixture.borrower_bank_id,
            cancelled_cheque_id=uuid4(),
            bank_verification_decision_id=self.fixture.bank_decision_id,
        )
        source = SimpleNamespace(
            source_bank_account_id=self.fixture.source_bank_id,
            active=True,
            bank_name="RBL Bank",
        )
        gate = Barrier(5)

        def contender(index):
            close_old_connections()
            try:
                actor = User.objects.get(pk=self.fixture.actor.pk)
                gate.wait(timeout=15)
                try:
                    result = initiate(
                        actor=actor,
                        loan_account_id=self.fixture.account_id,
                        payload={
                            "disbursement_amount": "400000.00",
                            "borrower_bank_account_id": str(
                                self.fixture.borrower_bank_id
                            ),
                            "source_bank_account_id": str(self.fixture.source_bank_id),
                            "final_verification_comments": f"Race contender {index}",
                        },
                        idempotency_key=f"race-initiation-{index}",
                    )
                    return ("won", result["disbursement_id"])
                except DisbursementConflict:
                    return ("conflict", None)
            finally:
                connections["default"].close()

        with (
            patch(
                "sfpcl_credit.disbursements.modules.disbursement_readiness."
                "DisbursementReadinessModule.evaluate",
                return_value=self.fixture._readiness(),
            ),
            patch(
                "sfpcl_credit.applications.modules.document_checklist_facts."
                "resolve_blank_cheque_bank_fact",
                return_value=bank,
            ),
            patch(
                "sfpcl_credit.configurations.modules.configuration_resolver."
                "resolve_source_bank_account",
                return_value=source,
            ),
            ThreadPoolExecutor(max_workers=5) as pool,
        ):
            results = list(pool.map(contender, range(5)))

        winners = [item for item in results if item[0] == "won"]
        self.assertEqual(len(winners), 1, results)
        self.assertEqual(len([item for item in results if item[0] == "conflict"]), 4)
        row = Disbursement.objects.get()
        self.assertEqual(str(row.pk), winners[0][1])
        self.assertEqual(row.cfc_task.related_entity_id, row.pk)
        self.assertEqual(row.initiation_audit.entity_id, row.pk)
        self.assertEqual(row.initiation_workflow_event.entity_id, row.pk)
        self.assertEqual(
            AuditLog.objects.filter(action="disbursement.initiated").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(workflow_name="DisbursementInitiated").count(),
            1,
        )
        self.assertEqual(
            Notification.objects.filter(
                notification_type="disbursement_authorisation"
            ).count(),
            1,
        )
