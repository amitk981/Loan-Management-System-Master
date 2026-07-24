from django.test import Client, TestCase
from django.utils import timezone
from uuid import uuid4

from sfpcl_credit.applications.models import LoanApplication
from sfpcl_credit.credit.models import LoanAppraisalNote, RiskAssessment
from sfpcl_credit.identity.models import (
    AuditLog,
    Permission,
    Role,
    RolePermission,
    Team,
    User,
    UserTeamMembership,
)
from sfpcl_credit.tests.api_contracts import assert_pagination_shape
from sfpcl_credit.members.models import Member
from sfpcl_credit.workflows.events import record_workflow_event
from sfpcl_credit.workflows.models import WorkflowTask
from sfpcl_credit.workflows.tasks import (
    reconcile_workflow_tasks,
    run_task_reconciliation_job,
    schedule_task_reconciliation,
    task_state_mapping,
)


class WorkflowTaskProjectionTests(TestCase):
    def setUp(self):
        role = Role.objects.create(
            role_code="credit_manager",
            role_name="Credit Manager",
            is_system_role=True,
            status="active",
        )
        self.actor = User.objects.create(
            full_name="Task Projection Actor",
            email="task.projection@sfpcl.example",
            status="active",
            primary_role=role,
        )
        self.member = Member.objects.create(
            member_number="MEM-TASK-001",
            member_type="individual_farmer",
            legal_name="Task Test Borrower",
            display_name="Task Test Borrower",
            folio_number="FOL-TASK-001",
            membership_status="active",
            pan_encrypted="test-only-encrypted-pan",
            pan_hash="task-test-pan-hash",
            kyc_status="verified",
            default_status="no_default",
            created_by_user=self.actor,
        )
        self.received_at = timezone.now() - timezone.timedelta(hours=4)
        self.application = LoanApplication.objects.create(
            application_reference_number="LO-TASK-001",
            member=self.member,
            borrower_type=self.member.member_type,
            received_by_user=self.actor,
            created_by_user=self.actor,
            required_loan_amount="125000.00",
            application_status=LoanApplication.STATUS_REFERENCE_GENERATED,
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
            submitted_at=self.received_at,
            created_at=self.received_at,
        )

    def test_reference_generation_creates_one_source_due_appraisal_task_on_replay(self):
        for _attempt in range(2):
            record_workflow_event(
                actor=self.actor,
                workflow_name="loan_application",
                entity_type="loan_application",
                entity_id=self.application.pk,
                from_state=LoanApplication.STATUS_SUBMITTED,
                to_state=LoanApplication.STATUS_REFERENCE_GENERATED,
                trigger_reason="Application number generated.",
            )

        task = WorkflowTask.objects.get()
        self.assertEqual(task.task_type, WorkflowTask.TYPE_APPRAISAL)
        self.assertEqual(task.linked_entity_type, "loan_application")
        self.assertEqual(task.linked_entity_id, self.application.pk)
        self.assertEqual(task.assigned_role_code, "deputy_manager_finance")
        self.assertEqual(task.status, WorkflowTask.STATUS_OPEN)
        self.assertEqual(task.borrower_name, self.member.display_name)
        self.assertEqual(task.amount, self.application.required_loan_amount)
        self.assertEqual(
            task.due_at,
            self.received_at + timezone.timedelta(days=2),
        )

    def test_all_eight_task_types_open_once_for_owner_role_and_close_on_exit(self):
        cases = (
            (
                "loan_application",
                "submitted",
                "incomplete_returned",
                WorkflowTask.TYPE_COMPLETENESS_CHECK,
                "deputy_manager_finance",
            ),
            (
                "loan_application",
                "reference_generated",
                "review_pending",
                WorkflowTask.TYPE_APPRAISAL,
                "deputy_manager_finance",
            ),
            (
                "loan_application",
                "submitted_to_sanction_committee",
                "approved_by_sanction_committee",
                WorkflowTask.TYPE_SANCTION,
                "cfo",
            ),
            (
                "document_checklist",
                "in_progress",
                "ready",
                WorkflowTask.TYPE_DOCUMENT_VERIFICATION,
                "compliance_team_member",
            ),
            (
                "sap_customer_profile_request",
                "draft",
                "completed",
                WorkflowTask.TYPE_SAP_SETUP,
                "senior_manager_finance",
            ),
            (
                "disbursement",
                "ready_for_disbursement",
                "disbursed",
                WorkflowTask.TYPE_DISBURSEMENT,
                "senior_manager_finance",
            ),
            (
                "repayment",
                "received",
                "posted",
                WorkflowTask.TYPE_REPAYMENT_POSTING,
                "credit_manager",
            ),
            (
                "default_case",
                "grace_period_expired",
                "resolved_by_repayment",
                WorkflowTask.TYPE_DEFAULT_REVIEW,
                "credit_manager",
            ),
        )

        for entity_type, open_state, closed_state, task_type, role_code in cases:
            with self.subTest(task_type=task_type):
                entity_id = uuid4()
                for _attempt in range(2):
                    record_workflow_event(
                        actor=self.actor,
                        workflow_name=entity_type,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        from_state=None,
                        to_state=open_state,
                    )
                task = WorkflowTask.objects.get(
                    linked_entity_type=entity_type,
                    linked_entity_id=entity_id,
                    task_type=task_type,
                )
                self.assertEqual(task.assigned_role_code, role_code)
                self.assertEqual(task.status, WorkflowTask.STATUS_OPEN)

                record_workflow_event(
                    actor=self.actor,
                    workflow_name=entity_type,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    from_state=open_state,
                    to_state=closed_state,
                )
                task.refresh_from_db()
                self.assertEqual(task.status, WorkflowTask.STATUS_CLOSED)
                self.assertIsNotNone(task.closed_at)

    def test_source_task_state_mapping_exposes_all_eight_owner_rules(self):
        mapping = task_state_mapping()

        self.assertEqual(set(mapping), WorkflowTask.TASK_TYPES)
        self.assertEqual(
            mapping[WorkflowTask.TYPE_APPRAISAL]["assigned_role_code"],
            "deputy_manager_finance",
        )
        self.assertEqual(
            mapping[WorkflowTask.TYPE_DOCUMENT_VERIFICATION]["assigned_team_code"],
            "compliance",
        )

    def test_appraisal_review_closes_return_reopens_and_terminal_paths_leave_no_stale_preparation(self):
        record_workflow_event(
            actor=self.actor,
            workflow_name="loan_application",
            entity_type="loan_application",
            entity_id=self.application.pk,
            from_state=LoanApplication.STATUS_SUBMITTED,
            to_state=LoanApplication.STATUS_REFERENCE_GENERATED,
        )
        risk = RiskAssessment.objects.create(
            loan_application=self.application,
            market_risk_rating="low",
            operational_risk_rating="low",
            borrower_risk_rating="low",
            overall_risk_rating="low",
            assessed_by_user=self.actor,
        )
        note = LoanAppraisalNote.objects.create(
            loan_application=self.application,
            prepared_by_user=self.actor,
            tat_due_at=self.application.created_at + timezone.timedelta(days=2),
            tat_status=LoanAppraisalNote.TAT_WITHIN,
            eligibility_assessment_id_snapshot=uuid4(),
            loan_limit_assessment_id_snapshot=uuid4(),
            borrower_summary="Source-backed borrower summary",
            eligibility_summary="Eligible",
            loan_limit_summary="Within retained limit",
            recommended_amount="100000.00",
            recommended_security_summary="Retained security summary",
            repayment_capacity_notes="Retained repayment capacity",
            risk_assessment=risk,
            recommendation="approve",
        )

        for to_state, expected_open in (
            (LoanAppraisalNote.STATUS_REVIEW_PENDING, False),
            (LoanAppraisalNote.STATUS_DRAFT, True),
            (LoanAppraisalNote.STATUS_REVIEWED, False),
            (LoanAppraisalNote.STATUS_REJECTED, False),
            (LoanAppraisalNote.STATUS_SUBMITTED_TO_SANCTION, False),
        ):
            record_workflow_event(
                actor=self.actor,
                workflow_name="appraisal_note",
                entity_type="loan_appraisal_note",
                entity_id=note.pk,
                from_state=None,
                to_state=to_state,
            )
            self.assertEqual(
                WorkflowTask.objects.filter(
                    linked_entity_type="loan_application",
                    linked_entity_id=self.application.pk,
                    task_type=WorkflowTask.TYPE_APPRAISAL,
                    status=WorkflowTask.STATUS_OPEN,
                ).exists(),
                expected_open,
            )

    def test_reconciliation_backfills_and_recomputes_overdue_without_duplicates(self):
        receipt_at = timezone.now() - timezone.timedelta(days=3)
        LoanApplication.objects.filter(pk=self.application.pk).update(
            submitted_at=receipt_at,
            created_at=receipt_at,
        )

        first = reconcile_workflow_tasks()
        second = reconcile_workflow_tasks()

        self.assertGreaterEqual(first["tasks_opened_or_refreshed"], 1)
        self.assertGreaterEqual(second["tasks_opened_or_refreshed"], 1)
        task = WorkflowTask.objects.get(
            linked_entity_type="loan_application",
            linked_entity_id=self.application.pk,
            task_type=WorkflowTask.TYPE_APPRAISAL,
            status=WorkflowTask.STATUS_OPEN,
        )
        self.assertEqual(
            WorkflowTask.objects.filter(
                linked_entity_type="loan_application",
                linked_entity_id=self.application.pk,
                task_type=WorkflowTask.TYPE_APPRAISAL,
                status=WorkflowTask.STATUS_OPEN,
            ).count(),
            1,
        )
        self.assertEqual(task.overdue_days, 1)

    def test_scheduled_reconciliation_uses_003j_job_lifecycle(self):
        from sfpcl_credit.scheduler.models import ScheduledJob

        job, created = schedule_task_reconciliation(
            due_at=timezone.now(),
            idempotency_key="workflow-task-reconciliation:2026-07-24",
        )
        replay, replay_created = schedule_task_reconciliation(
            due_at=timezone.now(),
            idempotency_key="workflow-task-reconciliation:2026-07-24",
        )
        result = run_task_reconciliation_job(job.pk)

        self.assertTrue(created)
        self.assertFalse(replay_created)
        self.assertEqual(replay.pk, job.pk)
        job.refresh_from_db()
        self.assertEqual(job.status, ScheduledJob.STATUS_SUCCEEDED)
        self.assertGreaterEqual(result["tasks_opened_or_refreshed"], 1)


class WorkflowTaskApiTests(TestCase):
    URL = "/api/v1/tasks/"

    def setUp(self):
        self.client = Client()
        self.role = Role.objects.create(
            role_code="credit_manager",
            role_name="Credit Manager",
            is_system_role=True,
            status="active",
        )
        self.user = User.objects.create(
            full_name="Task Inbox User",
            email="task.inbox@sfpcl.example",
            status="active",
            primary_role=self.role,
        )
        self.user.set_password("TaskInboxPass123!")
        self.user.save()
        self.team = Team.objects.create(
            team_code="credit_assessment",
            team_name="Credit Assessment Team",
            status="active",
        )
        UserTeamMembership.objects.create(user=self.user, team=self.team)
        now = timezone.now()
        self.due_today = WorkflowTask.objects.create(
            task_type=WorkflowTask.TYPE_APPRAISAL,
            linked_entity_type="loan_application",
            linked_entity_id=uuid4(),
            title="Review appraisal for LO-TASK-API-1",
            borrower_name="API Borrower",
            borrower_type="individual_farmer",
            amount="250000.00",
            assigned_role_code="credit_manager",
            assigned_team_code="credit_assessment",
            current_status="review_pending",
            due_at=now,
        )
        self.overdue = WorkflowTask.objects.create(
            task_type=WorkflowTask.TYPE_DEFAULT_REVIEW,
            linked_entity_type="loan_account",
            linked_entity_id=uuid4(),
            title="Review default for LN-TASK-API-2",
            borrower_name="Overdue Borrower",
            borrower_type="producer_institution",
            amount="750000.00",
            assigned_role_code="credit_manager",
            assigned_team_code="credit_assessment",
            current_status="grace_period_expired",
            due_at=now - timezone.timedelta(days=3),
            overdue_days=3,
            special_case=True,
            exception_required=True,
            priority=WorkflowTask.PRIORITY_HIGH,
        )

    def _headers(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            data={"email": self.user.email, "password": "TaskInboxPass123!"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return {
            "Authorization": f"Bearer {response.json()['data']['access_token']}"
        }

    def test_role_scoped_list_supports_s03_filters_pagination_and_columns(self):
        response = self.client.get(
            self.URL
            + "?task_type=appraisal&due_today=true&borrower_type=individual_farmer"
            + "&minimum_amount=200000&assigned_to_my_team=true",
            headers=self._headers(),
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        assert_pagination_shape(self, payload)
        self.assertEqual(len(payload["data"]), 1)
        row = payload["data"][0]
        self.assertEqual(row["task_id"], str(self.due_today.pk))
        self.assertEqual(row["task_reference"], self.due_today.task_reference)
        self.assertEqual(row["task_type"], WorkflowTask.TYPE_APPRAISAL)
        self.assertEqual(row["application_or_loan_id"], str(self.due_today.linked_entity_id))
        self.assertEqual(row["borrower"], "API Borrower")
        self.assertEqual(row["amount"], "250000.00")
        self.assertEqual(row["sla_tat"]["overdue_days"], 0)
        self.assertEqual(row["assigned_to"]["role_code"], "credit_manager")
        self.assertEqual(row["action"]["code"], "open")

        overdue = self.client.get(
            self.URL + "?overdue=true&special_case=true&exception_required=true",
            headers=self._headers(),
        )
        self.assertEqual(overdue.status_code, 200)
        self.assertEqual(
            [item["task_id"] for item in overdue.json()["data"]],
            [str(self.overdue.pk)],
        )

    def test_task_actions_enforce_reassign_permission_and_emit_audit_events(self):
        target = User.objects.create(
            full_name="Reassigned Reviewer",
            email="reassigned.reviewer@sfpcl.example",
            status="active",
            primary_role=self.role,
        )
        forbidden = self.client.post(
            f"{self.URL}{self.due_today.pk}/reassign/",
            data={"assigned_to_user_id": str(target.pk)},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(forbidden.status_code, 403)

        permission = Permission.objects.create(
            permission_code="users.team.manage",
            permission_name="Manage teams",
            module_name="users",
            risk_level="high",
        )
        RolePermission.objects.create(role=self.role, permission=permission)
        reassigned = self.client.post(
            f"{self.URL}{self.due_today.pk}/reassign/",
            data={"assigned_to_user_id": str(target.pk)},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(reassigned.status_code, 200)
        self.due_today.refresh_from_db()
        self.assertEqual(self.due_today.assigned_to_user, target)

        comment = self.client.post(
            f"{self.URL}{self.due_today.pk}/comments/",
            data={"comment": "Waiting for the revised eligibility attachment."},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(comment.status_code, 200)
        blocked = self.client.post(
            f"{self.URL}{self.due_today.pk}/block/",
            data={"reason": "Eligibility attachment is missing."},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(blocked.status_code, 200)
        unblocked = self.client.post(
            f"{self.URL}{self.due_today.pk}/unblock/",
            data={},
            content_type="application/json",
            headers=self._headers(),
        )
        self.assertEqual(unblocked.status_code, 200)

        self.assertEqual(
            set(
                AuditLog.objects.filter(entity_id=self.due_today.pk).values_list(
                    "action", flat=True
                )
            ),
            {
                "workflow_task.reassigned",
                "workflow_task.commented",
                "workflow_task.blocked",
                "workflow_task.unblocked",
            },
        )
        self.assertEqual(self.due_today.comments.count(), 1)

    def test_dashboard_returns_same_callers_open_tasks_in_section_43_shape(self):
        permission = Permission.objects.create(
            permission_code="management_readonly",
            permission_name="View management dashboard",
            module_name="dashboard",
            risk_level="medium",
        )
        RolePermission.objects.create(role=self.role, permission=permission)

        response = self.client.get("/api/v1/dashboard/", headers=self._headers())

        self.assertEqual(response.status_code, 200)
        tasks = response.json()["data"]["tasks"]
        self.assertEqual(len(tasks), 2)
        self.assertEqual(
            set(tasks[0]),
            {"task_type", "entity_id", "title", "due_at"},
        )
        self.assertEqual(
            {item["entity_id"] for item in tasks},
            {str(self.due_today.linked_entity_id), str(self.overdue.linked_entity_id)},
        )
