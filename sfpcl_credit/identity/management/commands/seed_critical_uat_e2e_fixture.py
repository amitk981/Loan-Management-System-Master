"""Seed guarded preconditions for the critical UAT Playwright tracer."""

import os
from datetime import date, datetime
from types import SimpleNamespace
from uuid import UUID

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from sfpcl_credit.compliance.models import (
    ComplianceControl,
    ComplianceEvidence,
    ComplianceTask,
)
from sfpcl_credit.configurations.models import InterestRateConfig
from sfpcl_credit.configurations.modules.interest_rate_configuration import activate
from sfpcl_credit.documents.models import DocumentFile
from sfpcl_credit.identity.models import Permission, Role, RolePermission, User
from sfpcl_credit.interest.models import InterestInvoiceConfiguration
from sfpcl_credit.legal_documents.models import LoanDocument
from sfpcl_credit.legal_documents.selectors import (
    current_loan_term_document_for_update,
)
from sfpcl_credit.loans.models import LoanAccount, RepaymentSchedule


PASSWORD = "CriticalUat123!"
ACTOR_IDS = {
    "cfo": UUID("00000000-0000-4000-8300-000000000001"),
    "accounts": UUID("00000000-0000-4000-8300-000000000002"),
    "rate_checker": UUID("00000000-0000-4000-8300-000000000003"),
    "auditor": UUID("00000000-0000-4000-8300-000000000004"),
}
INTEREST_RATE_CONFIG_ID = UUID("00000000-0000-4000-8370-000000000001")
INTEREST_INVOICE_CONFIG_ID = UUID("00000000-0000-4000-8370-000000000002")
CONTROL_IDS = {
    "SECTION_186_LIMIT": UUID("00000000-0000-4000-8310-000000000001"),
    "NBFC_PRINCIPAL_TEST": UUID("00000000-0000-4000-8310-000000000002"),
}
TASK_IDS = {
    "SECTION_186_LIMIT": UUID("00000000-0000-4000-8320-000000000001"),
    "NBFC_PRINCIPAL_TEST": UUID("00000000-0000-4000-8320-000000000002"),
}
DOCUMENT_IDS = {
    "SECTION_186_LIMIT": UUID("00000000-0000-4000-8330-000000000001"),
    "NBFC_PRINCIPAL_TEST": UUID("00000000-0000-4000-8330-000000000002"),
}
EVIDENCE_IDS = {
    "SECTION_186_LIMIT": UUID("00000000-0000-4000-8340-000000000001"),
    "NBFC_PRINCIPAL_TEST": UUID("00000000-0000-4000-8340-000000000002"),
}


class Command(BaseCommand):
    help = (
        "Seed deterministic critical-UAT actors and preconditions in an isolated "
        "local Playwright database."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        self._enforce_e2e_guard()
        cfo = self._actor(
            actor_id=ACTOR_IDS["cfo"],
            email="e2e.uat.cfo@sfpcl.example",
            full_name="Critical UAT CFO",
            role_code="cfo",
        )
        accounts = self._actor(
            actor_id=ACTOR_IDS["accounts"],
            email="e2e.uat.accounts@sfpcl.example",
            full_name="Critical UAT Accounts",
            role_code="accounts_head",
        )
        rate_checker = self._actor(
            actor_id=ACTOR_IDS["rate_checker"],
            email="e2e.uat.rate.checker@sfpcl.example",
            full_name="Critical UAT Rate Checker",
            role_code="system_admin",
        )
        self._actor(
            actor_id=ACTOR_IDS["auditor"],
            email="e2e.uat.auditor@sfpcl.example",
            full_name="Critical UAT Internal Auditor",
            role_code="internal_auditor",
        )
        RolePermission.objects.get_or_create(
            role=cfo.primary_role,
            permission=Permission.objects.get(permission_code="approvals.matrix.read"),
        )
        RolePermission.objects.get_or_create(
            role=rate_checker.primary_role,
            permission=Permission.objects.get(
                permission_code="communications.communication.send"
            ),
        )
        account = self._schedule()
        self._subsidiary_repayment_precondition(account)
        self._interest_precondition(
            accounts=accounts,
            rate_checker=rate_checker,
        )
        for control_code in CONTROL_IDS:
            self._compliance_precondition(
                control_code=control_code,
                maker=cfo,
                reviewer=accounts,
            )
        self.stdout.write("Critical UAT E2E fixture seeded.")

    @staticmethod
    def _actor(*, actor_id, email, full_name, role_code):
        try:
            role = Role.objects.get(role_code=role_code)
        except Role.DoesNotExist as exc:
            raise CommandError(
                "Run seed_role_catalogue before seed_critical_uat_e2e_fixture."
            ) from exc
        actor, _created = User.objects.update_or_create(
            user_id=actor_id,
            defaults={
                "email": email,
                "full_name": full_name,
                "status": User.ACTIVE_STATUS,
                "primary_role": role,
            },
        )
        actor.set_password(PASSWORD)
        actor.save(update_fields=["password_hash"])
        return actor

    @staticmethod
    def _schedule():
        try:
            account = LoanAccount.objects.get(loan_account_number="LN-REAL-OWNER-001")
        except LoanAccount.DoesNotExist as exc:
            raise CommandError(
                "Run seed_epic_009_e2e_fixture before seed_critical_uat_e2e_fixture."
            ) from exc
        RepaymentSchedule.objects.update_or_create(
            loan_account=account,
            installment_number=1,
            defaults={
                "due_date": date(2026, 6, 30),
                "principal_due": account.sanctioned_amount,
                "interest_due": "0.00",
                "charges_due": "0.00",
                "total_due": account.sanctioned_amount,
                "schedule_status": "pending",
            },
        )
        return account

    @staticmethod
    def _subsidiary_repayment_precondition(account):
        agreement = (
            LoanDocument.objects.select_for_update()
            .filter(
                loan_application_id=account.loan_application_id,
                document_type="tri_party_agreement",
            )
            .order_by("-created_at", "-loan_document_id")
            .first()
        )
        if agreement is None:
            raise CommandError(
                "The Epic 009 fixture must include a tri-party agreement for "
                "critical UAT subsidiary repayment."
            )
        if agreement.execution_status != "executed":
            agreement.execution_status = "executed"
            agreement.save(update_fields=["execution_status"])
        if current_loan_term_document_for_update(
            application_id=account.loan_application_id,
            document_type="tri_party_agreement",
        ) is None:
            raise CommandError(
                "The Epic 009 tri-party agreement is not current verified loan-term "
                "evidence for critical UAT subsidiary repayment."
            )

    @staticmethod
    def _interest_precondition(*, accounts, rate_checker):
        rate, _created = InterestRateConfig.objects.get_or_create(
            interest_rate_config_id=INTEREST_RATE_CONFIG_ID,
            defaults={
                "version_number": "RATE-CRITICAL-UAT-1",
                "rate_type": "floating",
                "effective_rate": "9.2500",
                "effective_from": date(2026, 4, 1),
                "effective_to": date(2027, 3, 31),
                "benchmark_name": "RBL_BASE",
                "spread_rate": "1.2500",
                "reset_frequency": "annual",
                "communication_required": False,
                "board_approval_reference": "BOARD-CRITICAL-UAT-RATE-1",
                "created_by_user": accounts,
            },
        )
        activate(
            actor=rate_checker,
            request=SimpleNamespace(META={}, headers={}),
            interest_rate_config_id=rate.pk,
            idempotency_key="activate-critical-uat-rate-1",
        )
        InterestInvoiceConfiguration.objects.get_or_create(
            interest_invoice_configuration_id=INTEREST_INVOICE_CONFIG_ID,
            defaults={
                "version_number": "INV-CRITICAL-UAT-1",
                "effective_from": date(2026, 4, 1),
                "effective_to": date(2027, 3, 31),
                "calculation_method": "simple_daily",
                "day_count_basis": 365,
                "monetary_rounding_mode": "half_up",
                "monetary_precision": "0.01",
                "rounding_application_boundary": "whole_decision",
                "tax_rate": "0.0000",
                "fixed_fee_amount": "0.00",
                "owner_role_codes": ["accounts_head"],
                "status": "active",
                "approved_by_user": rate_checker,
            },
        )

    @staticmethod
    def _compliance_precondition(*, control_code, maker, reviewer):
        control, _created = ComplianceControl.objects.update_or_create(
            compliance_control_id=CONTROL_IDS[control_code],
            defaults={
                "control_code": control_code,
                "control_name": f"Critical UAT {control_code}",
                "control_area": "statutory",
                "legal_basis": "Synthetic source-backed UAT evidence.",
                "control_type": ComplianceControl.TYPE_DETECTIVE,
                "frequency": ComplianceControl.FREQUENCY_QUARTERLY,
                "owner_role_code": maker.primary_role.role_code,
                "owner_user": maker,
                "reviewer_user": reviewer,
                "first_due_date": date(2026, 6, 30),
                "evidence_required": "Accepted synthetic quarterly evidence.",
                "risk_if_missed": "Critical UAT statutory calculation is not evidenced.",
                "status": ComplianceControl.STATUS_ACTIVE,
            },
        )
        task, _created = ComplianceTask.objects.update_or_create(
            compliance_task_id=TASK_IDS[control_code],
            defaults={
                "control": control,
                "task_period": "2026-Q2",
                "due_date": date(2026, 6, 30),
                "assigned_to_user": maker,
                "reviewer_user": reviewer,
                "task_status": ComplianceTask.STATUS_EVIDENCE_SUBMITTED,
                "remarks": "Deterministic public-action precondition.",
            },
        )
        document, _created = DocumentFile.objects.update_or_create(
            document_id=DOCUMENT_IDS[control_code],
            defaults={
                "file_name": f"{control_code.lower()}-uat.pdf",
                "file_extension": ".pdf",
                "mime_type": "application/pdf",
                "file_size_bytes": 128,
                "storage_provider": "local",
                "storage_key": f"e2e/critical-uat/{control_code.lower()}.pdf",
                "checksum_sha256": f"critical-uat-{control_code.lower()}",
                "uploaded_by_user": maker,
                "uploaded_at": timezone.make_aware(datetime(2026, 7, 1, 10, 0)),
                "sensitivity_level": DocumentFile.SENSITIVITY_RESTRICTED,
            },
        )
        evidence, _created = ComplianceEvidence.objects.get_or_create(
            compliance_evidence_id=EVIDENCE_IDS[control_code],
            defaults={
                "task": task,
                "evidence_type": control_code,
                "document": document,
                "summary": "Accepted synthetic quarterly source evidence.",
                "source_owner": "finance",
                "source_entity_type": "compliance_task",
                "source_entity_id": task.pk,
                "source_period": task.task_period,
                "submitted_by_user": maker,
                "review_status": ComplianceEvidence.REVIEW_ACCEPTED,
                "reviewed_by_user": reviewer,
                "reviewed_at": timezone.make_aware(datetime(2026, 7, 1, 11, 0)),
                "review_comments": "Accepted for deterministic UAT calculation.",
            },
        )
        if task.current_evidence_id != evidence.pk:
            task.current_evidence = evidence
            task.save(update_fields=["current_evidence"])

    @staticmethod
    def _env_true(name):
        return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}

    @classmethod
    def _enforce_e2e_guard(cls):
        if not settings.ENABLE_DEMO_SURFACES:
            raise CommandError(
                "seed_critical_uat_e2e_fixture is disabled by deployment settings."
            )
        if (
            not cls._env_true("SFPCL_DEBUG")
            or not cls._env_true("SFPCL_ALLOW_E2E_SEED")
        ):
            raise CommandError(
                "seed_critical_uat_e2e_fixture is for an isolated local Playwright "
                "database only. Set SFPCL_DEBUG=true and SFPCL_ALLOW_E2E_SEED=true."
            )
