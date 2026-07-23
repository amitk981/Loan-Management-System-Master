from datetime import timedelta
from uuid import uuid4

from django.test import Client, TestCase
from django.utils import timezone

from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant
from sfpcl_credit.identity.models import Permission, Role, RolePermission, User


class AuditorEpic011ApiTests(TestCase):
    password = "AuditorReadOnly123!"

    def setUp(self):
        self.client = Client()
        self.role = Role.objects.create(
            role_code="internal_auditor",
            role_name="Internal Auditor",
        )
        self.auditor = User.objects.create(
            full_name="Epic 011 Auditor",
            email="epic-011-auditor@example.test",
            primary_role=self.role,
            password_hash="",
        )
        self.auditor.set_password(self.password)
        self.auditor.save(update_fields=["password_hash"])
        for code in (
            "reports.compliance.read",
            "defaults.case.read",
            "closure.archive.read",
            "compliance.control.read",
            "compliance.task.read",
            "compliance.section186.read",
            "compliance.nbfc_test.read",
            "compliance.grievance.read",
        ):
            permission, _created = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": code.split(".", 1)[0],
                    "risk_level": "low",
                },
            )
            RolePermission.objects.create(role=self.role, permission=permission)
        ApprovalCaseReadScopeGrant.objects.create(
            role=self.role,
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
            status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
        )

    def test_scoped_auditor_receives_empty_action_free_epic_011_projection(self):
        response = self.client.get(
            "/api/v1/auditor/epic-011/",
            **self._auth(),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            response.json()["data"],
            {
                "summary": {
                    "default_cases": 0,
                    "closures": 0,
                    "compliance_items": 0,
                    "grievances": 0,
                },
                "default_cases": [],
                "closures": [],
                "compliance_items": [],
                "grievances": [],
            },
        )
        self.assertNotIn("available_actions", response.content.decode())

    def test_auditor_without_active_scope_cannot_query_epic_011_collections(self):
        from sfpcl_credit.identity.models import AuditLog

        ApprovalCaseReadScopeGrant.objects.filter(role=self.role).update(
            status=ApprovalCaseReadScopeGrant.STATUS_INACTIVE
        )
        auth = self._auth()

        for path in (
            "/api/v1/auditor/epic-011/",
            "/api/v1/compliance-controls/",
            "/api/v1/compliance-tasks/",
            "/api/v1/kyc-reviews/",
            "/api/v1/compliance/section-186-trackers/",
            "/api/v1/compliance/nbfc-principal-tests/",
            "/api/v1/grievances/",
        ):
            with self.subTest(path=path):
                before = AuditLog.objects.count()
                response = self.client.get(path, **auth)
                self.assertEqual(response.status_code, 403, response.content)
                self.assertEqual(AuditLog.objects.count(), before + 1)
                denial = AuditLog.objects.latest("created_at")
                self.assertEqual(denial.actor_user_id, self.auditor.pk)
                self.assertEqual(denial.new_value_json["method"], "GET")
                self.assertEqual(denial.new_value_json["path"], path)

    def test_scoped_auditor_reads_each_epic_011_family_with_immutable_references(self):
        from sfpcl_credit.closure.models import LoanClosure
        from sfpcl_credit.compliance.models import ComplianceControl, Grievance
        from sfpcl_credit.defaults.models import DefaultCase
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.tests.test_loan_schedule_ledger_api import (
            LoanScheduleLedgerApiTests,
        )
        from sfpcl_credit.workflows.models import WorkflowEvent

        fixture = LoanScheduleLedgerApiTests(
            "test_authorised_reader_gets_ordered_decimal_schedule_truth"
        )
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        account = fixture.account
        owner = account.loan_application.created_by_user
        schedule = RepaymentSchedule.objects.create(
            loan_account=account,
            installment_number=1,
            due_date=account.repayment_date,
            principal_due="1000.00",
            interest_due="100.00",
            charges_due="0.00",
            total_due="1100.00",
            schedule_status="pending",
        )
        default_id = uuid4()
        default_audit = AuditLog.objects.create(
            actor_user=owner,
            action="default.case_opened",
            entity_type="default_case",
            entity_id=default_id,
        )
        default_case = DefaultCase.objects.create(
            default_case_id=default_id,
            loan_account=account,
            member=account.member,
            repayment_schedule=schedule,
            trigger_event="missed_principal_repayment",
            scheduled_due_date=schedule.due_date,
            grace_period_start_date=schedule.due_date,
            grace_period_end_date=schedule.due_date + timedelta(days=90),
            default_case_status="grace_period_active",
            reason="Scheduled principal was not received.",
            opened_by_user=owner,
            opening_audit=default_audit,
        )
        default_event = WorkflowEvent.objects.create(
            workflow_name="default_case",
            entity_type="default_case",
            entity_id=default_case.pk,
            to_state="grace_period_active",
            triggered_by_user=owner,
        )
        closure_id = uuid4()
        closure_audit = AuditLog.objects.create(
            actor_user=owner,
            action="closure.loan.closed",
            entity_type="loan_closure",
            entity_id=closure_id,
        )
        closure_event = WorkflowEvent.objects.create(
            workflow_name="loan_closure",
            entity_type="loan_closure",
            entity_id=closure_id,
            from_state="repaid",
            to_state="financially_closed",
            triggered_by_user=owner,
        )
        closure = LoanClosure.objects.create(
            loan_closure_id=closure_id,
            loan_account=account,
            member=account.member,
            closure_type="full_repayment",
            closure_stage="financially_closed",
            closure_notes="Financial closure evidence retained.",
            principal_paid_flag=True,
            interest_paid_flag=True,
            charges_paid_flag=True,
            total_outstanding_at_closure="0.00",
            readiness_snapshot_json={"checks": []},
            closed_by_user=owner,
            closed_by_role_code=owner.primary_role.role_code,
            idempotency_key_digest="a" * 64,
            payload_digest="b" * 64,
            close_audit=closure_audit,
            workflow_event=closure_event,
        )
        reviewer_role, _created = Role.objects.get_or_create(
            role_code="cfo",
            defaults={"role_name": "CFO"},
        )
        reviewer = User.objects.create(
            full_name="Control Reviewer",
            email="control-reviewer@example.test",
            primary_role=reviewer_role,
            password_hash="",
        )
        control = ComplianceControl.objects.create(
            control_code="RECOVERY_CONDUCT",
            control_name="Recovery conduct review",
            control_area="recovery_conduct",
            legal_basis="Fair-practice control.",
            control_type="detective",
            frequency="quarterly",
            owner_role_code=owner.primary_role.role_code,
            owner_user=owner,
            reviewer_user=reviewer,
            first_due_date=timezone.localdate(),
            evidence_required="Recovery interaction evidence.",
            risk_if_missed="Conduct exception.",
            status="active",
        )
        grievance = Grievance.objects.create(
            grievance_reference="GRV-2026-AUDITOR0001",
            idempotency_key="auditor-populated-grievance",
            request_digest="c" * 64,
            member=account.member,
            loan_account=account,
            default_case=default_case,
            grievance_category="recovery_conduct_issue",
            description="Recovery interaction requires review.",
            received_date=timezone.localdate(),
            received_channel="form",
            assigned_to_user=owner,
            resolution_due_date=timezone.localdate() + timedelta(days=7),
            created_by_user=owner,
            created_by_role_code=owner.primary_role.role_code,
        )

        response = self.client.get("/api/v1/auditor/epic-011/", **self._auth())

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertEqual(data["summary"]["default_cases"], 1)
        self.assertEqual(data["summary"]["closures"], 1)
        self.assertEqual(data["summary"]["compliance_items"], 1)
        self.assertEqual(data["summary"]["grievances"], 1)
        self.assertEqual(data["default_cases"][0]["default_case_id"], str(default_case.pk))
        self.assertIn(str(default_audit.pk), data["default_cases"][0]["audit_references"])
        self.assertIn(str(default_event.pk), data["default_cases"][0]["workflow_references"])
        self.assertEqual(data["closures"][0]["loan_closure_id"], str(closure.pk))
        self.assertIn(str(closure_audit.pk), data["closures"][0]["audit_references"])
        self.assertIn(str(closure_event.pk), data["closures"][0]["workflow_references"])
        self.assertEqual(data["compliance_items"][0]["record_id"], str(control.pk))
        self.assertEqual(data["grievances"][0]["grievance_id"], str(grievance.pk))
        self.assertNotIn("available_actions", response.content.decode())

    def test_auditor_permission_and_http_method_matrix_has_no_operational_mutation(self):
        import json

        from sfpcl_credit.closure.models import LoanClosure
        from sfpcl_credit.compliance.models import ComplianceControl, Grievance
        from sfpcl_credit.defaults.models import DefaultCase
        from sfpcl_credit.identity.catalogue import ROLE_PERMISSIONS
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.workflows.models import WorkflowEvent

        forbidden_permissions = {
            permission
            for permission in ROLE_PERMISSIONS["internal_auditor"]
            if permission.rsplit(".", 1)[-1]
            in {
                "create",
                "manage",
                "update",
                "review",
                "resolve",
                "close",
                "issue",
                "return",
                "archive",
                "initiate",
                "complete",
                "approve",
                "invoke",
            }
        }
        self.assertEqual(forbidden_permissions, set())
        arbitrary = uuid4()
        calls = (
            ("post", f"/api/v1/loan-accounts/{arbitrary}/default-cases/open/"),
            ("post", f"/api/v1/default-cases/{arbitrary}/assess/"),
            ("post", f"/api/v1/default-cases/{arbitrary}/grant-extension/"),
            ("post", f"/api/v1/default-cases/{arbitrary}/recovery-decision/"),
            ("post", f"/api/v1/default-cases/{arbitrary}/non-payment-note/"),
            ("post", f"/api/v1/non-payment-notes/{arbitrary}/submit-to-sanction-committee/"),
            ("post", f"/api/v1/recovery-decisions/{arbitrary}/actions/"),
            ("post", f"/api/v1/recovery-actions/{arbitrary}/complete/"),
            ("post", f"/api/v1/loan-accounts/{arbitrary}/closure/"),
            ("post", f"/api/v1/loan-closures/{arbitrary}/noc/"),
            ("post", f"/api/v1/loan-closures/{arbitrary}/security-return/"),
            ("post", f"/api/v1/loan-closures/{arbitrary}/archive/"),
            ("post", "/api/v1/compliance-controls/"),
            ("patch", f"/api/v1/compliance-controls/{arbitrary}/"),
            ("post", "/api/v1/compliance-tasks/"),
            ("patch", f"/api/v1/compliance-tasks/{arbitrary}/"),
            ("post", f"/api/v1/compliance-tasks/{arbitrary}/evidence/"),
            ("post", f"/api/v1/compliance-evidence/{arbitrary}/review/"),
            ("post", "/api/v1/compliance/money-lending-law-reviews/"),
            ("post", "/api/v1/grievances/"),
            ("patch", f"/api/v1/grievances/{arbitrary}/"),
            ("post", f"/api/v1/grievances/{arbitrary}/resolve/"),
            ("patch", f"/api/v1/kyc-reviews/{arbitrary}/"),
            ("post", f"/api/v1/kyc-reviews/{arbitrary}/remind/"),
            ("post", f"/api/v1/kyc-reviews/{arbitrary}/complete/"),
            ("post", "/api/v1/compliance/section-186-trackers/"),
            ("post", f"/api/v1/compliance/section-186-trackers/{arbitrary}/submit-for-review/"),
            ("post", f"/api/v1/compliance/section-186-trackers/{arbitrary}/review/"),
            ("post", "/api/v1/compliance/nbfc-principal-tests/"),
            ("post", f"/api/v1/compliance/nbfc-principal-tests/{arbitrary}/submit-for-review/"),
            ("post", f"/api/v1/compliance/nbfc-principal-tests/{arbitrary}/review/"),
        )
        auth = self._auth()
        counts_before = (
            DefaultCase.objects.count(),
            LoanClosure.objects.count(),
            ComplianceControl.objects.count(),
            Grievance.objects.count(),
        )
        for method, path in calls:
            with self.subTest(method=method, path=path):
                audit_ids = set(
                    AuditLog.objects.values_list("audit_log_id", flat=True)
                )
                workflow_ids = set(
                    WorkflowEvent.objects.values_list("workflow_event_id", flat=True)
                )
                response = getattr(self.client, method)(
                    path,
                    data=json.dumps({}),
                    content_type="application/json",
                    HTTP_IDEMPOTENCY_KEY="auditor-mutation-denied",
                    **auth,
                )
                self.assertEqual(response.status_code, 403, response.content)
                new_audits = AuditLog.objects.exclude(
                    audit_log_id__in=audit_ids
                )
                new_workflows = WorkflowEvent.objects.exclude(
                    workflow_event_id__in=workflow_ids
                )
                self.assertTrue(
                    all("denied" in action for action in new_audits.values_list("action", flat=True))
                )
                self.assertTrue(
                    all(
                        "denied" in state
                        for state in new_workflows.values_list("to_state", flat=True)
                    )
                )
        self.assertEqual(
            (
                DefaultCase.objects.count(),
                LoanClosure.objects.count(),
                ComplianceControl.objects.count(),
                Grievance.objects.count(),
            ),
            counts_before,
        )

    def _auth(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={
                "email": self.auditor.email,
                "password": self.password,
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {
            "HTTP_AUTHORIZATION": f"Bearer {response.json()['data']['access_token']}"
        }
