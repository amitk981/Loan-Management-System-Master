"""Seed the isolated real-Django fixture used by Epic 009 browser acceptance.

This command is deliberately unavailable without both local E2E guards.  The fixture builders
reuse the repository's public-API contract setup so the retained browser proof exercises the same
immutable owner evidence as the backend regression suite, rather than maintaining a second hand-
assembled representation of SAP, documentation, security, and disbursement truth.
"""

import os
from pathlib import Path
from unittest.mock import patch
from uuid import UUID

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError
from django.test import RequestFactory

from sfpcl_credit.communications.models import Notification
from sfpcl_credit.documents.services import store_document_upload
from sfpcl_credit.identity.models import Permission, User


E2E_PASSWORD = "ChecklistPass123!"
FINANCE_EMAIL = "e2e.epic009.finance@sfpcl.example"
CREDIT_EMAIL = "e2e.epic009.credit@sfpcl.example"
CFC_EMAIL = "e2e.epic009.cfc@sfpcl.example"
BORROWER_EMAIL = "e2e.epic009.borrower@sfpcl.example"
MISSING_ACCOUNT_ID = UUID("00000000-0000-4000-8000-000000000999")


class _PersistentDirectory:
    """TemporaryDirectory-compatible wrapper that keeps E2E evidence after seeding."""

    def __init__(self, *args, **kwargs):
        root = Path(settings.DOCUMENT_STORAGE_ROOT)
        root.mkdir(parents=True, exist_ok=True)
        self.name = str(root)

    def cleanup(self):
        return None


class Command(BaseCommand):
    help = (
        "Idempotently seed guarded Epic 009 staff, SAP, loan-account, readiness, and transfer "
        "evidence for real-Django Playwright acceptance."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--make-ready",
            action="store_true",
            help="Advance the isolated fixture from its named source-bank blocker to ready.",
        )
        parser.add_argument(
            "--prepare-transfer",
            action="store_true",
            help="Create the isolated restricted transfer document after CFC approval.",
        )

    def handle(self, *args, **options):
        self._enforce_e2e_guard()
        if options["make_ready"]:
            self._make_ready()
            return
        if options["prepare_transfer"]:
            self._prepare_transfer()
            return
        if User.objects.filter(email=FINANCE_EMAIL).exists():
            self.stdout.write("Epic 009 E2E fixture already seeded.")
            return

        # The contract setup uses TemporaryDirectory because ordinary tests must clean files.
        # Browser acceptance must retain those same synthetic files while runserver is alive.
        with patch("tempfile.TemporaryDirectory", _PersistentDirectory):
            facts = self._seed_ready_account()
            self._seed_browser_documents_and_notifications(facts)
            self._validate_account(facts, "browser notifications")
            self._set_source_bank_status(facts["ready"]["source_bank"], "inactive")

        self.stdout.write(
            "Epic 009 E2E fixture seeded: completed SAP, sanctioned blocked account, "
            "Credit Manager, Senior Finance, and CFC actors."
        )

    @staticmethod
    def _env_true(name):
        return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}

    @classmethod
    def _enforce_e2e_guard(cls):
        if not cls._env_true("SFPCL_DEBUG") or not cls._env_true(
            "SFPCL_ALLOW_E2E_SEED"
        ):
            raise CommandError(
                "seed_epic_009_e2e_fixture is for isolated local Playwright databases only. "
                "Set SFPCL_DEBUG=true and SFPCL_ALLOW_E2E_SEED=true to run it."
            )

    @staticmethod
    def _seed_ready_account():
        # Imported only behind the E2E guards: production startup never imports test helpers.
        from sfpcl_credit.tests.test_final_documentation_approval_api import (
            FinalDocumentationApprovalApiTests,
        )

        owner = FinalDocumentationApprovalApiTests(
            "test_disbursement_readiness_real_owners_reach_a126_then_all_pass"
        )
        owner.setUp()
        finance = owner.finance
        credit = owner.credit
        # Establish deterministic browser identities before owner services freeze them.
        Command._make_browser_actor(finance, FINANCE_EMAIL)
        Command._make_browser_actor(credit, CREDIT_EMAIL)
        ready = owner._real_owner_initiation_fixture(stop_before_initiation=True)
        ready["account"].member.email = BORROWER_EMAIL
        ready["account"].member.save(update_fields=["email"])
        from sfpcl_credit.loans.modules.loan_account_read import resolve_creation_truth
        from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
            get_account_customer_code,
        )

        if resolve_creation_truth(account=ready["account"]) is None:
            raise CommandError("Epic 009 fixture produced no current loan creation truth.")
        if get_account_customer_code(
            application_id=ready["account"].loan_application_id,
            member_id=ready["account"].member_id,
            customer_code_id=ready["account"].sap_customer_code_id,
        ) is None:
            raise CommandError("Epic 009 fixture produced no current SAP completion truth.")
        owner._grant(
            finance,
            "finance.loan_account.read",
            "communications.notification.read",
            "finance.disbursement.mark_success",
            "finance.disbursement.send_advice",
        )
        advice_permission = Permission.objects.get(
            permission_code="finance.disbursement.send_advice"
        )
        advice_permission.risk_level = Permission.RISK_HIGH
        advice_permission.save(update_fields=["risk_level"])
        owner._grant(
            credit,
            "finance.loan_account.read",
            "communications.notification.read",
        )

        cfc = owner.fixture._user(
            "chief_financial_controller", "Epic 009 Browser CFC"
        )
        Command._make_browser_actor(cfc, CFC_EMAIL)
        cfc.approval_authority_type = "chief_financial_controller"
        cfc.save(update_fields=["approval_authority_type"])
        owner._grant(
            cfc,
            "finance.disbursement.authorise",
            "finance.disbursement.mark_success",
            "finance.loan_account.read",
            "communications.notification.read",
        )
        return {
            "owner": owner,
            "ready": ready,
            "finance": finance,
            "credit": credit,
            "cfc": cfc,
        }

    @staticmethod
    def _make_browser_actor(user, email):
        user.email = email
        user.status = "active"
        user.set_password(E2E_PASSWORD)
        user.save(update_fields=["email", "status", "password_hash"])

    @staticmethod
    def _seed_browser_documents_and_notifications(facts):
        Notification.objects.create(
            notification_type="e2e_missing_loan_account",
            category="finance",
            severity=Notification.SEVERITY_WARNING,
            title="Open inaccessible loan account",
            message="Exercises a genuine nondisclosing Django response.",
            related_entity_type="loan_account",
            related_entity_id=MISSING_ACCOUNT_ID,
            action_label="Open loan account",
            action_url=f"/loan-accounts/{MISSING_ACCOUNT_ID}",
            recipient_user=facts["finance"],
        )

    @staticmethod
    def _validate_account(facts, stage):
        from sfpcl_credit.processes.loan_account_360 import _project
        from sfpcl_credit.loans.modules.loan_account_read import resolve_creation_truth
        from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
            get_account_customer_code,
        )

        facts["ready"]["account"].refresh_from_db()
        if _project(facts["ready"]["account"]) is None:
            account = facts["ready"]["account"]
            raise CommandError(
                "Epic 009 account projection became incoherent after "
                f"{stage}: creation={resolve_creation_truth(account=account) is not None}, "
                "sap="
                f"{get_account_customer_code(application_id=account.loan_application_id, member_id=account.member_id, customer_code_id=account.sap_customer_code_id) is not None}."
            )

    @staticmethod
    def _set_source_bank_status(bank, status):
        bank.status = status
        bank.save(update_fields=["status"])

    @classmethod
    def _make_ready(cls):
        from sfpcl_credit.configurations.models import SourceBankAccountGovernance

        if not User.objects.filter(email=FINANCE_EMAIL).exists():
            raise CommandError("Seed the Epic 009 E2E fixture before advancing it.")
        governance = SourceBankAccountGovernance.objects.select_related(
            "bank_account"
        ).get(activated_by_user__email=FINANCE_EMAIL, status="active")
        cls._set_source_bank_status(governance.bank_account, "active")

    @classmethod
    def _prepare_transfer(cls):
        from sfpcl_credit.loans.models import LoanAccount

        if Notification.objects.filter(
            notification_type="e2e_transfer_evidence"
        ).exists():
            return
        finance = User.objects.get(email=FINANCE_EMAIL)
        account = LoanAccount.objects.get(loan_account_number="LN-REAL-OWNER-001")
        evidence = store_document_upload(
            user=finance,
            request=RequestFactory().post(
                "/api/v1/documents/", REMOTE_ADDR="127.0.0.1"
            ),
            uploaded_file=SimpleUploadedFile(
                "epic-009-transfer-evidence.pdf",
                b"%PDF-1.4 synthetic Epic 009 transfer evidence",
                content_type="application/pdf",
            ),
            document_category="finance",
            sensitivity_level="restricted",
            related_entity_type="loan_application",
            related_entity_id=account.loan_application_id,
        )
        Notification.objects.create(
            notification_type="e2e_transfer_evidence",
            category="finance",
            severity=Notification.SEVERITY_INFO,
            title="Epic 009 transfer evidence",
            message="Synthetic restricted evidence for the isolated browser flow.",
            related_entity_type="document_file",
            related_entity_id=evidence.pk,
            recipient_user=finance,
        )
