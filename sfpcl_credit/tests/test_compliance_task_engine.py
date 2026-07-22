from datetime import date

from django.test import TestCase

from sfpcl_credit.identity.models import Role, User


class ComplianceTaskEngineTests(TestCase):
    def setUp(self):
        self.owner_role = Role.objects.create(
            role_code="company_secretary", role_name="Company Secretary"
        )
        self.reviewer_role = Role.objects.create(
            role_code="cfo", role_name="Chief Financial Officer"
        )
        self.owner = User.objects.create(
            full_name="Compliance Owner",
            email="compliance-owner@example.test",
            primary_role=self.owner_role,
            password_hash="unused",
        )
        self.reviewer = User.objects.create(
            full_name="Compliance Reviewer",
            email="compliance-reviewer@example.test",
            primary_role=self.reviewer_role,
            password_hash="unused",
        )

    def test_r7_catalogue_source_map_covers_each_required_control_area(self):
        from sfpcl_credit.compliance.catalogue import R7_CONTROL_CATALOGUE

        self.assertEqual(len(R7_CONTROL_CATALOGUE), 11)
        self.assertSetEqual(
            {item[0] for item in R7_CONTROL_CATALOGUE},
            {
                "MEMBER_ONLY_LENDING", "SECTION_186_LIMIT", "NBFC_PRINCIPAL_TEST",
                "KYC_AML", "INTEREST_DISCLOSURE", "STAMP_DUTY", "MONEY_LENDING_ANNUAL",
                "ACCOUNTING_REPORTING", "RECOVERY_CONDUCT", "DATA_PROTECTION",
                "RECORD_RETENTION",
            },
        )

    def test_monthly_generation_is_due_and_exact_replay_creates_one_task(self):
        from sfpcl_credit.compliance.models import ComplianceControl, ComplianceTask
        from sfpcl_credit.compliance.modules.compliance_task_engine import (
            ComplianceTaskEngine,
        )

        control = ComplianceControl.objects.create(
            control_code="ACCOUNTING_MONTHLY",
            control_name="Monthly accounting review",
            control_area="accounting",
            legal_basis="Approved accounting control catalogue.",
            control_type=ComplianceControl.TYPE_DETECTIVE,
            frequency=ComplianceControl.FREQUENCY_MONTHLY,
            owner_role_code=self.owner_role.role_code,
            owner_user=self.owner,
            reviewer_user=self.reviewer,
            first_due_date=date(2026, 7, 31),
            evidence_required="SAP report and Board pack.",
            risk_if_missed="Reporting control overdue.",
            status=ComplianceControl.STATUS_ACTIVE,
        )

        first = ComplianceTaskEngine.generate_due_tasks(as_of_date=date(2026, 7, 31))
        replay = ComplianceTaskEngine.generate_due_tasks(as_of_date=date(2026, 7, 31))
        late = ComplianceTaskEngine.generate_due_tasks(as_of_date=date(2026, 8, 1))

        self.assertEqual(first.created_count, 1)
        self.assertEqual(replay.created_count, 0)
        self.assertEqual(late.created_count, 0)
        task = ComplianceTask.objects.get(control=control)
        self.assertEqual(task.task_period, "2026-07")
        self.assertEqual(task.due_date, date(2026, 7, 31))
        self.assertEqual(task.assigned_to_user, self.owner)
        self.assertEqual(task.reviewer_user, self.reviewer)
        self.assertEqual(task.task_status, ComplianceTask.STATUS_OVERDUE)

    def test_each_frequency_generates_stable_periods_and_one_overdue_escalation(self):
        from sfpcl_credit.communications.models import Notification
        from sfpcl_credit.compliance.models import ComplianceControl, ComplianceTask
        from sfpcl_credit.compliance.modules.compliance_task_engine import ComplianceTaskEngine
        from sfpcl_credit.scheduler.models import ScheduledJob

        controls = [
            ("MONTHLY", ComplianceControl.FREQUENCY_MONTHLY, date(2026, 1, 31)),
            ("QUARTERLY", ComplianceControl.FREQUENCY_QUARTERLY, date(2026, 3, 31)),
            ("ANNUAL", ComplianceControl.FREQUENCY_ANNUAL, date(2026, 3, 31)),
            ("ONGOING", ComplianceControl.FREQUENCY_ONGOING, date(2026, 1, 1)),
        ]
        for code, frequency, first_due_date in controls:
            ComplianceControl.objects.create(
                control_code=code,
                control_name=code.title(),
                control_area="compliance",
                legal_basis="Approved control catalogue.",
                control_type=ComplianceControl.TYPE_DETECTIVE,
                frequency=frequency,
                owner_role_code=self.owner_role.role_code,
                owner_user=self.owner,
                reviewer_user=self.reviewer,
                first_due_date=first_due_date,
                evidence_required="Governed evidence.",
                risk_if_missed="Escalate overdue control.",
            )

        run = ComplianceTaskEngine.generate_due_tasks(as_of_date=date(2026, 7, 1))
        replay = ComplianceTaskEngine.generate_due_tasks(as_of_date=date(2026, 7, 1))

        self.assertEqual(run.created_count, 10)
        self.assertEqual(replay.created_count, 0)
        self.assertSetEqual(
            set(ComplianceTask.objects.values_list("task_period", flat=True)),
            {
                "2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06",
                "2026-Q1", "2026-Q2", "FY2025-26", "ongoing",
            },
        )
        self.assertEqual(Notification.objects.filter(notification_type="compliance_overdue").count(), 10)
        job = ScheduledJob.objects.get(idempotency_key="compliance-task-generation:2026-07-01")
        self.assertEqual(job.status, ScheduledJob.STATUS_SUCCEEDED)

    def test_governed_evidence_is_submitted_then_accepted_by_distinct_reviewer(self):
        from sfpcl_credit.compliance.models import ComplianceControl, ComplianceEvidence, ComplianceTask
        from sfpcl_credit.compliance.modules.compliance_task_engine import ComplianceTaskEngine
        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.identity.models import Permission, RolePermission

        for role, code in (
            (self.owner_role, "compliance.evidence.submit"),
            (self.reviewer_role, "compliance.evidence.review"),
        ):
            permission = Permission.objects.create(
                permission_code=code,
                permission_name=code,
                module_name="compliance",
                risk_level="high",
            )
            RolePermission.objects.create(role=role, permission=permission)
        control = ComplianceControl.objects.create(
            control_code="RECORD_RETENTION",
            control_name="Record retention annual audit",
            control_area="records",
            legal_basis="Approved retention control.",
            control_type=ComplianceControl.TYPE_DETECTIVE,
            frequency=ComplianceControl.FREQUENCY_ANNUAL,
            owner_role_code=self.owner_role.role_code,
            owner_user=self.owner,
            reviewer_user=self.reviewer,
            first_due_date=date(2026, 6, 30),
            evidence_required="Restricted audit report.",
            risk_if_missed="Retention assurance overdue.",
        )
        task = ComplianceTask.objects.create(
            control=control,
            task_period="2026",
            due_date=date(2026, 6, 30),
            assigned_to_user=self.owner,
            reviewer_user=self.reviewer,
            task_status=ComplianceTask.STATUS_DUE,
        )
        document = DocumentFile.objects.create(
            file_name="retention-audit.pdf",
            mime_type="application/pdf",
            storage_provider="local",
            storage_key="governed/compliance/retention-audit.pdf",
            uploaded_by_user=self.owner,
            sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED,
        )

        submitted = ComplianceTaskEngine.submit_evidence(
            actor=self.owner,
            task_id=task.pk,
            payload={
                "evidence_type": "audit_report",
                "document_id": str(document.pk),
                "summary": "Annual retention audit completed.",
            },
        )
        reviewed = ComplianceTaskEngine.review_evidence(
            actor=self.reviewer,
            task_id=task.pk,
            decision="accepted",
            comments="Evidence matches the configured period and control.",
        )

        evidence = ComplianceEvidence.objects.get(pk=submitted.current_evidence_id)
        self.assertEqual(evidence.review_status, ComplianceEvidence.REVIEW_ACCEPTED)
        self.assertEqual(reviewed.task_status, ComplianceTask.STATUS_COMPLETED)
        self.assertIsNotNone(reviewed.closed_at)
        with self.assertRaisesMessage(ValueError, "Accepted compliance evidence is immutable"):
            evidence.summary = "changed"
            evidence.save()
