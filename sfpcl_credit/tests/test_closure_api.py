import json
from datetime import date

from django.core.exceptions import ValidationError
from django.test import Client, TestCase

from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.loans.models import LoanAccount


class LoanClosureApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_loan_account_reads_api import LoanAccountReadApiTests

        fixture = LoanAccountReadApiTests(
            "test_sanctioned_list_and_detail_are_exact_paginated_zero_write_projections"
        )
        fixture.setUp()
        self.fixture = fixture.fixture
        self.account = fixture.account
        LoanAccount.objects.filter(pk=self.account.pk).update(
            loan_account_status="partially_repaid",
            principal_outstanding="0.00",
            interest_outstanding="0.00",
            charges_outstanding="0.00",
            total_outstanding="0.00",
        )
        self.actor = self.fixture._user("credit_manager", "Closure Credit Manager")
        self.fixture._grant(
            self.actor,
            "closure.readiness.read",
            "closure.loan.close",
        )
        self.auth = self.fixture._auth(self.actor)
        self.client = Client()

    def test_zero_canonical_balances_return_named_readiness_without_writes(self):
        before_audits = AuditLog.objects.count()

        response = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/closure-readiness/",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertTrue(data["ready_for_closure"])
        self.assertEqual(data["total_outstanding"], "0.00")
        self.assertEqual(
            [check["code"] for check in data["checks"]],
            [
                "principal_paid",
                "interest_paid_or_approved_adjustment",
                "charges_paid",
                "ledger_reconciled",
                "recovery_clear",
                "security_tasks_identified",
            ],
        )
        self.assertTrue(all(check["status"] == "pass" for check in data["checks"]))
        self.assertFalse(data["interest_adjustment_applied"])
        self.assertIn("security_return_required", data)
        self.assertEqual(AuditLog.objects.count(), before_audits)

    def test_full_repayment_close_freezes_fresh_facts_and_creates_controlled_requirements(self):
        from sfpcl_credit.closure.models import ClosureRequirement, LoanClosure
        from sfpcl_credit.loans.models import LoanStatusHistory
        from sfpcl_credit.workflows.models import WorkflowEvent

        response = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/closure/",
            data=json.dumps(
                {
                    "closure_type": "full_repayment",
                    "closure_notes": "Principal, interest and charges verified as fully repaid.",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="close-account-001",
            HTTP_X_REQUEST_ID="req-close-account-001",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        closure = LoanClosure.objects.get(loan_account=self.account)
        account = LoanAccount.objects.get(pk=self.account.pk)
        self.assertEqual(data["loan_closure_id"], str(closure.pk))
        self.assertEqual(data["loan_account_status"], "closed")
        self.assertEqual(data["closure_stage"], "financially_closed")
        self.assertNotEqual(data["closure_stage"], "fully_closed_and_archived")
        self.assertEqual(closure.total_outstanding_at_closure, 0)
        self.assertEqual(closure.readiness_snapshot_json["total_outstanding"], "0.00")
        self.assertTrue(closure.principal_paid_flag)
        self.assertTrue(closure.interest_paid_flag)
        self.assertTrue(closure.charges_paid_flag)
        self.assertEqual(account.loan_account_status, "closed")
        self.assertEqual(account.closed_at, closure.closed_at)
        requirements = {
            row.requirement_type: row.requirement_status
            for row in ClosureRequirement.objects.filter(loan_closure=closure)
        }
        self.assertEqual(requirements["noc"], "pending")
        self.assertEqual(requirements["archive"], "pending")
        self.assertIn(requirements["security_return"], {"pending", "not_applicable"})
        self.assertEqual(data["noc_required"], True)
        self.assertEqual(data["archive_required"], True)
        self.assertEqual(
            LoanStatusHistory.objects.filter(
                loan_account=self.account,
                from_status="partially_repaid",
                to_status="closed",
            ).count(),
            1,
        )
        self.assertEqual(
            AuditLog.objects.filter(action="closure.loan.financially_closed").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="loan_closure", to_state="financially_closed"
            ).count(),
            1,
        )

    def test_each_financial_and_ledger_blocker_is_named_and_prevents_close(self):
        from sfpcl_credit.closure.models import LoanClosure
        from sfpcl_credit.loans.models import Repayment

        cases = (
            ("principal_outstanding", "principal_paid"),
            ("interest_outstanding", "interest_paid_or_approved_adjustment"),
            ("charges_outstanding", "charges_paid"),
        )
        for index, (field, failed_code) in enumerate(cases, start=1):
            with self.subTest(field=field):
                balances = {
                    "principal_outstanding": "0.00",
                    "interest_outstanding": "0.00",
                    "charges_outstanding": "0.00",
                    "total_outstanding": "1.00",
                }
                balances[field] = "1.00"
                LoanAccount.objects.filter(pk=self.account.pk).update(**balances)
                response = self.client.get(
                    f"/api/v1/loan-accounts/{self.account.pk}/closure-readiness/",
                    **self.auth,
                )
                self.assertEqual(response.status_code, 200, response.content)
                checks = {row["code"]: row["status"] for row in response.json()["data"]["checks"]}
                self.assertEqual(checks[failed_code], "fail")
                close = self._close(idempotency_key=f"blocked-balance-{index}")
                self.assertEqual(close.status_code, 409, close.content)
                self.assertFalse(LoanClosure.objects.exists())
                self.assertNotEqual(
                    LoanAccount.objects.get(pk=self.account.pk).loan_account_status,
                    "closed",
                )

        LoanAccount.objects.filter(pk=self.account.pk).update(
            principal_outstanding="0.00",
            interest_outstanding="0.00",
            charges_outstanding="0.00",
            total_outstanding="0.00",
        )
        capture_audit = AuditLog.objects.create(
            actor_user=self.actor,
            action="finance.repayment.captured",
            entity_type="repayment",
        )
        Repayment.objects.create(
            loan_account=self.account,
            member_id=self.account.member_id,
            repayment_source="direct_farmer",
            amount_received="1.00",
            received_date=date(2026, 7, 22),
            payment_method="neft",
            bank_reference_number="CLOSURE-PENDING-001",
            bank_reference_number_normalized="closure-pending-001",
            remarks="Pending allocation blocks closure.",
            allocation_status="pending",
            sap_posting_status="pending",
            captured_by_user=self.actor,
            idempotency_key_digest="1" * 64,
            payload_digest="2" * 64,
            capture_audit=capture_audit,
        )
        readiness = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/closure-readiness/", **self.auth
        )
        checks = {row["code"]: row["status"] for row in readiness.json()["data"]["checks"]}
        self.assertEqual(checks["ledger_reconciled"], "fail")
        self.assertEqual(self._close(idempotency_key="blocked-ledger").status_code, 409)
        self.assertFalse(LoanClosure.objects.exists())

    def test_close_rejects_forged_or_stale_readiness_and_audits_fresh_denial(self):
        from sfpcl_credit.closure.models import LoanClosure
        from sfpcl_credit.workflows.models import WorkflowEvent

        forged = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/closure/",
            data=json.dumps(
                {
                    "closure_type": "full_repayment",
                    "closure_notes": "Client attempts to assert a zero balance.",
                    "total_outstanding": "0.00",
                    "ready_for_closure": True,
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="forged-readiness",
            **self.auth,
        )
        self.assertEqual(forged.status_code, 400, forged.content)
        self.assertIn("total_outstanding", forged.json()["error"]["field_errors"])
        self.assertFalse(LoanClosure.objects.exists())

        ready = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/closure-readiness/", **self.auth
        )
        self.assertTrue(ready.json()["data"]["ready_for_closure"])
        LoanAccount.objects.filter(pk=self.account.pk).update(
            principal_outstanding="1.00", total_outstanding="1.00"
        )
        stale = self._close(idempotency_key="stale-readiness")
        self.assertEqual(stale.status_code, 409, stale.content)
        self.assertFalse(LoanClosure.objects.exists())
        self.assertEqual(
            AuditLog.objects.filter(action="closure.loan.close_denied").count(), 2
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(to_state="financial_close_denied").count(), 2
        )

    def test_exact_replay_returns_one_close_and_changed_or_unsupported_request_is_rejected(self):
        from sfpcl_credit.closure.models import ClosureRequirement, LoanClosure

        first = self._close(idempotency_key="close-replay-001")
        replay = self._close(idempotency_key="close-replay-001")
        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(
            first.json()["data"]["loan_closure_id"],
            replay.json()["data"]["loan_closure_id"],
        )
        self.assertTrue(replay.json()["data"]["idempotency_replayed"])
        changed = self._close(
            idempotency_key="close-replay-001",
            notes="A changed closure request must not replay.",
        )
        self.assertEqual(changed.status_code, 409, changed.content)
        self.assertEqual(LoanClosure.objects.count(), 1)
        self.assertEqual(ClosureRequirement.objects.count(), 3)

        unsupported = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/closure/",
            data=json.dumps(
                {"closure_type": "recovery", "closure_notes": "Unsupported close route."}
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="unsupported-close",
            **self.auth,
        )
        self.assertEqual(unsupported.status_code, 400, unsupported.content)

    def test_financially_closed_account_rejects_direct_balance_mutation(self):
        response = self._close(idempotency_key="close-before-direct-mutation")
        self.assertEqual(response.status_code, 200, response.content)
        account = LoanAccount.objects.get(pk=self.account.pk)
        account.principal_outstanding = 1
        account.total_outstanding = 1

        with self.assertRaisesMessage(
            ValidationError, "Closed loan accounts are read-only"
        ):
            account.save(update_fields=["principal_outstanding", "total_outstanding"])
        with self.assertRaisesMessage(
            ValidationError, "Closed loan accounts are read-only"
        ):
            LoanAccount.objects.filter(pk=account.pk).update(
                principal_outstanding=1, total_outstanding=1
            )
        account = LoanAccount.objects.get(pk=account.pk)
        account.principal_outstanding = 1
        account.total_outstanding = 1
        with self.assertRaisesMessage(
            ValidationError, "Closed loan accounts are read-only"
        ):
            LoanAccount.objects.bulk_update(
                [account], ["principal_outstanding", "total_outstanding"]
            )

    def test_wrong_workflow_stage_is_nondisclosing_and_retains_denial_evidence(self):
        from sfpcl_credit.closure.models import LoanClosure
        from sfpcl_credit.workflows.models import WorkflowEvent

        LoanAccount.objects.filter(pk=self.account.pk).update(
            loan_account_status="active"
        )
        response = self._close(idempotency_key="wrong-stage-close")

        self.assertEqual(response.status_code, 404, response.content)
        self.assertFalse(LoanClosure.objects.exists())
        self.assertEqual(
            AuditLog.objects.filter(action="closure.loan.close_denied").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(to_state="financial_close_denied").count(), 1
        )

    def test_company_secretary_with_security_scope_can_financially_close(self):
        from sfpcl_credit.identity.models import Role, User
        from sfpcl_credit.security_instruments.models import SecurityPackage

        SecurityPackage.objects.get_or_create(
            loan_application_id=self.account.loan_application_id,
            defaults={
                "security_status": SecurityPackage.STATUS_COMPLETE,
                "poa_required_flag": True,
                "security_summary": "Governed closure security scope.",
            },
        )
        role, _ = Role.objects.get_or_create(
            role_code="company_secretary",
            defaults={"role_name": "Company Secretary", "status": "active"},
        )
        actor = User.objects.create(
            full_name="Closure Company Secretary",
            email="closure-cs@sfpcl.example",
            status="active",
            primary_role=role,
        )
        actor.set_password(self.fixture.password)
        actor.save()
        self.fixture._grant(
            actor, "closure.readiness.read", "closure.loan.close"
        )
        auth = self.fixture._auth(actor)

        response = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/closure/",
            data=json.dumps(
                {
                    "closure_type": "full_repayment",
                    "closure_notes": "Company Secretary verified financial closure.",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="company-secretary-close",
            **auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["data"]["loan_account_status"], "closed")

    def test_auditor_can_read_but_cannot_close_and_permission_without_role_is_denied(self):
        from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant

        auditor = self.fixture._user("internal_auditor", "Closure Auditor")
        self.fixture._grant(auditor, "closure.readiness.read", "closure.loan.close")
        ApprovalCaseReadScopeGrant.objects.create(
            role=auditor.primary_role,
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
            status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
        )
        auditor_auth = self.fixture._auth(auditor)
        allowed_read = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/closure-readiness/",
            **auditor_auth,
        )
        self.assertEqual(allowed_read.status_code, 200, allowed_read.content)
        self.assertEqual(
            self.client.post(
                f"/api/v1/loan-accounts/{self.account.pk}/closure/",
                data=json.dumps(
                    {"closure_type": "full_repayment", "closure_notes": "Auditor denied."}
                ),
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="auditor-close-denied",
                **auditor_auth,
            ).status_code,
            403,
        )
        wrong_role = self.fixture._user("field_officer", "Closure Permission Only")
        self.fixture._grant(wrong_role, "closure.readiness.read", "closure.loan.close")
        wrong_auth = self.fixture._auth(wrong_role)
        self.assertEqual(
            self.client.get(
                f"/api/v1/loan-accounts/{self.account.pk}/closure-readiness/",
                **wrong_auth,
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.post(
                f"/api/v1/loan-accounts/{self.account.pk}/closure/",
                data=json.dumps(
                    {"closure_type": "full_repayment", "closure_notes": "Denied role."}
                ),
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY="denied-role-close",
                **wrong_auth,
            ).status_code,
            403,
        )
        self.assertEqual(
            AuditLog.objects.filter(action="closure.loan.close_denied").count(), 2
        )

    def _close(
        self,
        *,
        idempotency_key,
        notes="Principal, interest and charges verified as fully repaid.",
    ):
        return self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/closure/",
            data=json.dumps(
                {"closure_type": "full_repayment", "closure_notes": notes}
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=idempotency_key,
            **self.auth,
        )


class LoanClosurePendingRecoveryTests(TestCase):
    def test_pending_recovery_action_is_a_named_close_blocker(self):
        from sfpcl_credit.identity.models import Permission, RolePermission
        from sfpcl_credit.recovery.models import RecoveryAction
        from sfpcl_credit.tests.test_recovery_action_api import RecoveryActionApiTests

        fixture = RecoveryActionApiTests(
            "test_company_secretary_initiates_exact_approved_sh4_with_governed_evidence"
        )
        fixture.setUp()
        decision, _ = fixture._approved_decision()
        actor, auth = fixture._executor()
        evidence = fixture._recovery_evidence(actor)
        initiated = Client().post(
            f"/api/v1/recovery-decisions/{decision['recovery_decision_id']}/actions/",
            data=json.dumps(fixture._initiation_payload(evidence)),
            content_type="application/json",
            **auth,
        )
        self.assertEqual(initiated.status_code, 200, initiated.content)
        account = fixture.account
        LoanAccount.objects.filter(pk=account.pk).update(
            principal_outstanding="0.00",
            interest_outstanding="0.00",
            charges_outstanding="0.00",
            total_outstanding="0.00",
            loan_account_status="under_recovery",
        )
        for code in ("closure.readiness.read", "closure.loan.close"):
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "closure",
                    "risk_level": "critical",
                },
            )
            RolePermission.objects.get_or_create(
                role=actor.primary_role, permission=permission
            )

        readiness = Client().get(
            f"/api/v1/loan-accounts/{account.pk}/closure-readiness/", **auth
        )
        self.assertEqual(readiness.status_code, 200, readiness.content)
        checks = {row["code"]: row["status"] for row in readiness.json()["data"]["checks"]}
        self.assertEqual(checks["recovery_clear"], "fail")
        close = Client().post(
            f"/api/v1/loan-accounts/{account.pk}/closure/",
            data=json.dumps(
                {
                    "closure_type": "full_repayment",
                    "closure_notes": "Pending recovery must block financial closure.",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="pending-recovery-close",
            **auth,
        )
        self.assertEqual(close.status_code, 409, close.content)
        self.assertEqual(RecoveryAction.objects.get().action_status, "pending")
