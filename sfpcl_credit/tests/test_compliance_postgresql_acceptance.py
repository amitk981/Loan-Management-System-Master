from concurrent.futures import ThreadPoolExecutor
from datetime import date
from unittest import skipUnless

from django.db import close_old_connections, connection
from django.test import TransactionTestCase

from sfpcl_credit.communications.models import Notification
from sfpcl_credit.compliance.models import (
    ComplianceControl,
    ComplianceEvidence,
    ComplianceTask,
    KYCReview,
    NbfcPrincipalBusinessTest,
    Section186Tracker,
)
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import Permission, Role, RolePermission, User
from sfpcl_credit.members.models import KycProfile, Member


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class ComplianceControlSchedulerPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def test_concurrent_scheduler_runs_create_one_task_and_notification(self):
        owner_role = Role.objects.create(role_code="company_secretary", role_name="CS")
        reviewer_role = Role.objects.create(role_code="cfo", role_name="CFO")
        owner = User.objects.create(full_name="Owner", email="pg-owner@example.test", primary_role=owner_role)
        reviewer = User.objects.create(full_name="Reviewer", email="pg-reviewer@example.test", primary_role=reviewer_role)
        ComplianceControl.objects.create(
            control_code="PG_RACE", control_name="PostgreSQL race", control_area="compliance",
            legal_basis="Acceptance fixture", control_type="detective", frequency="annual",
            owner_role_code=owner_role.role_code, owner_user=owner, reviewer_user=reviewer,
            first_due_date=date(2026, 3, 31), evidence_required="Governed evidence",
            risk_if_missed="Escalate", status="active",
        )

        def run():
            close_old_connections()
            from sfpcl_credit.compliance.modules.compliance_task_engine import ComplianceTaskEngine
            try:
                return ComplianceTaskEngine.generate_due_tasks(as_of_date=date(2026, 4, 1))
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            list(executor.map(lambda _value: run(), range(2)))

        self.assertEqual(ComplianceTask.objects.count(), 1)
        self.assertEqual(Notification.objects.filter(notification_type="compliance_overdue").count(), 1)


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class RekycSchedulerPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def test_concurrent_scheduler_runs_create_one_review_task_and_reminder_identity(self):
        owner_role = Role.objects.create(role_code="credit_manager", role_name="Credit Manager")
        reviewer_role = Role.objects.create(
            role_code="compliance_team_member", role_name="Compliance Team Member"
        )
        owner = User.objects.create(
            full_name="KYC Owner", email="pg-kyc-owner@example.test", primary_role=owner_role
        )
        reviewer = User.objects.create(
            full_name="KYC Reviewer",
            email="pg-kyc-reviewer@example.test",
            primary_role=reviewer_role,
        )
        ComplianceControl.objects.create(
            control_code="KYC_AML",
            control_name="KYC and AML review",
            control_area="kyc",
            legal_basis="Two-year governed KYC review.",
            control_type="detective",
            frequency="ongoing",
            owner_role_code=owner_role.role_code,
            owner_user=owner,
            reviewer_user=reviewer,
            first_due_date=date(2026, 1, 1),
            evidence_required="Governed KYC verification.",
            risk_if_missed="KYC becomes stale.",
        )
        member = Member.objects.create(
            member_type="individual_farmer",
            legal_name="PostgreSQL KYC Member",
            display_name="PostgreSQL KYC Member",
            folio_number="PG-KYC-1",
            membership_status="active",
            pan_encrypted="encrypted-pan",
            pan_hash="pg-kyc-pan-hash",
            kyc_status="verified",
            default_status="no_default",
        )
        from datetime import datetime, timezone as dt_timezone

        KycProfile.objects.create(
            party_type="member",
            party_id=member.pk,
            kyc_status="verified",
            ckyc_consent_flag=True,
            risk_rating="low",
            last_verified_at=datetime(2024, 2, 29, 9, 0, tzinfo=dt_timezone.utc),
            last_verified_by_user=owner,
            rekyc_due_date=date(2026, 2, 28),
        )

        def run():
            close_old_connections()
            from sfpcl_credit.compliance.modules.kyc_review_tracker import KYCReviewTracker

            try:
                return KYCReviewTracker.generate_due_reviews(as_of_date=date(2026, 2, 28))
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            list(executor.map(lambda _value: run(), range(2)))

        self.assertEqual(KYCReview.objects.count(), 1)
        self.assertEqual(ComplianceTask.objects.filter(kyc_review__isnull=False).count(), 1)
        self.assertEqual(
            Notification.objects.filter(notification_type="kyc_review_due").count(), 1
        )


@skipUnless(connection.vendor == "postgresql", "PostgreSQL concurrency acceptance")
class StatutoryTrackerPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def test_concurrent_creates_retain_one_exact_result_per_type_and_period(self):
        owner_role = Role.objects.create(role_code="cfo", role_name="CFO")
        reviewer_role = Role.objects.create(
            role_code="internal_auditor", role_name="Internal Auditor"
        )
        owner = User.objects.create(
            full_name="Statutory Owner",
            email="pg-statutory-owner@example.test",
            primary_role=owner_role,
        )
        reviewer = User.objects.create(
            full_name="Statutory Reviewer",
            email="pg-statutory-reviewer@example.test",
            primary_role=reviewer_role,
        )
        for code in (
            "compliance.section186.create",
            "compliance.nbfc_test.create",
        ):
            permission = Permission.objects.create(
                permission_code=code,
                permission_name=code,
                module_name="compliance",
                risk_level=Permission.RISK_CRITICAL,
            )
            RolePermission.objects.create(role=owner_role, permission=permission)
        document = DocumentFile.objects.create(
            file_name="pg-quarterly-financials.pdf",
            storage_provider="local",
            storage_key="governed/compliance/pg-quarterly-financials.pdf",
            uploaded_by_user=owner,
            sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED,
        )

        section_task, section_evidence = self._evidence(
            "SECTION_186_LIMIT", owner, reviewer, document
        )
        nbfc_task, nbfc_evidence = self._evidence(
            "NBFC_PRINCIPAL_TEST", owner, reviewer, document
        )
        section_payload = {
            "financial_year": "FY2026-27",
            "quarter": "Q1",
            "paid_up_capital_amount": "100.00",
            "free_reserves_amount": "50.00",
            "securities_premium_amount": "10.00",
            "total_loans_exposure_amount": "80.00",
            "compliance_evidence_id": str(section_evidence.pk),
        }
        nbfc_payload = {
            "financial_year": "FY2026-27",
            "quarter": "Q1",
            "financial_assets_amount": "51.00",
            "total_assets_amount": "100.00",
            "financial_income_amount": "51.00",
            "gross_income_amount": "100.00",
            "early_warning_threshold_ratio": "40.0000",
            "compliance_evidence_id": str(nbfc_evidence.pk),
        }

        def race(module, task_id, payload):
            def calculate(_value):
                close_old_connections()
                try:
                    return module.calculate(
                        actor=User.objects.get(pk=owner.pk),
                        period_id=task_id,
                        payload=payload,
                    ).pk
                finally:
                    close_old_connections()
            with ThreadPoolExecutor(max_workers=2) as executor:
                return list(executor.map(calculate, range(2)))

        from sfpcl_credit.compliance.modules.nbfc_principal_business_test import (
            NbfcPrincipalBusinessTestModule,
        )
        from sfpcl_credit.compliance.modules.section186_tracker import Section186TrackerModule

        section_ids = race(Section186TrackerModule, section_task.pk, section_payload)
        nbfc_ids = race(NbfcPrincipalBusinessTestModule, nbfc_task.pk, nbfc_payload)
        self.assertEqual(section_ids[0], section_ids[1])
        self.assertEqual(nbfc_ids[0], nbfc_ids[1])
        self.assertEqual(Section186Tracker.objects.count(), 1)
        self.assertEqual(NbfcPrincipalBusinessTest.objects.count(), 1)

    @staticmethod
    def _evidence(control_code, owner, reviewer, document):
        control = ComplianceControl.objects.create(
            control_code=control_code, control_name=control_code, control_area="statutory",
            legal_basis="PostgreSQL acceptance fixture.", control_type="detective",
            frequency="quarterly", owner_role_code=owner.primary_role.role_code,
            owner_user=owner, reviewer_user=reviewer, first_due_date=date(2026, 6, 30),
            evidence_required="Restricted quarterly financials.",
            risk_if_missed="Statutory assessment overdue.",
        )
        task = ComplianceTask.objects.create(
            control=control, task_period="2026-Q2", due_date=date(2026, 6, 30),
            assigned_to_user=owner, reviewer_user=reviewer,
            task_status=ComplianceTask.STATUS_COMPLETED,
        )
        evidence = ComplianceEvidence.objects.create(
            task=task, evidence_type="quarterly_financials", document=document,
            summary="PostgreSQL acceptance financials.", source_owner="documents",
            source_entity_type="document_file", source_entity_id=document.pk,
            source_period=task.task_period, submitted_by_user=owner,
            review_status=ComplianceEvidence.REVIEW_ACCEPTED, reviewed_by_user=reviewer,
        )
        task.current_evidence = evidence
        task.save(update_fields=["current_evidence"])
        return task, evidence
