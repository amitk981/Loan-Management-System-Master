import json
import tempfile
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant
from sfpcl_credit.compliance.models import ComplianceEvidence, ComplianceTask
from sfpcl_credit.configurations.models import InterestRateConfig
from sfpcl_credit.identity.models import User
from sfpcl_credit.interest.models import InterestInvoiceConfiguration
from sfpcl_credit.legal_documents.selectors import (
    current_loan_term_document_for_update,
)
from sfpcl_credit.loans.models import LoanAccount, RepaymentSchedule


class CriticalUatE2eSeedTests(TestCase):
    def test_seed_refuses_without_isolated_e2e_guards(self):
        with self.assertRaisesMessage(CommandError, "isolated local Playwright"):
            call_command("seed_critical_uat_e2e_fixture")

    def test_seed_is_idempotent_and_builds_only_public_journey_preconditions(self):
        with tempfile.TemporaryDirectory() as storage_root, override_settings(
            DOCUMENT_STORAGE_ROOT=storage_root
        ), patch.dict(
            "os.environ",
            {"SFPCL_DEBUG": "true", "SFPCL_ALLOW_E2E_SEED": "true"},
        ):
            call_command("seed_epic_009_e2e_fixture")
            call_command("seed_critical_uat_e2e_fixture")
            counts = (
                User.objects.filter(email__startswith="e2e.uat.").count(),
                RepaymentSchedule.objects.count(),
                ComplianceTask.objects.filter(task_period="2026-Q2").count(),
                ComplianceEvidence.objects.filter(source_period="2026-Q2").count(),
                InterestRateConfig.objects.filter(
                    version_number="RATE-CRITICAL-UAT-1",
                    status=InterestRateConfig.STATUS_ACTIVE,
                ).count(),
                InterestInvoiceConfiguration.objects.filter(
                    version_number="INV-CRITICAL-UAT-1",
                ).count(),
            )
            call_command("seed_critical_uat_e2e_fixture")

        self.assertEqual(counts, (4, 1, 2, 2, 1, 1))
        self.assertEqual(
            (
                User.objects.filter(email__startswith="e2e.uat.").count(),
                RepaymentSchedule.objects.count(),
                ComplianceTask.objects.filter(task_period="2026-Q2").count(),
                ComplianceEvidence.objects.filter(source_period="2026-Q2").count(),
                InterestRateConfig.objects.filter(
                    version_number="RATE-CRITICAL-UAT-1",
                    status=InterestRateConfig.STATUS_ACTIVE,
                ).count(),
                InterestInvoiceConfiguration.objects.filter(
                    version_number="INV-CRITICAL-UAT-1",
                ).count(),
            ),
            counts,
        )
        self.assertTrue(
            User.objects.get(email="e2e.uat.cfo@sfpcl.example").check_password(
                "CriticalUat123!"
            )
        )
        auditor = User.objects.get(email="e2e.uat.auditor@sfpcl.example")
        self.assertEqual(auditor.primary_role.role_code, "internal_auditor")
        self.assertTrue(auditor.check_password("CriticalUat123!"))
        self.assertTrue(
            ApprovalCaseReadScopeGrant.objects.filter(
                role=auditor.primary_role,
                scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
                status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
            ).exists()
        )
        schedule = RepaymentSchedule.objects.get()
        self.assertEqual(str(schedule.principal_due), "400000.00")
        self.assertEqual(schedule.due_date.isoformat(), "2026-06-30")
        account = LoanAccount.objects.get(loan_account_number="LN-REAL-OWNER-001")
        self.assertIsNotNone(
            current_loan_term_document_for_update(
                application_id=account.loan_application_id,
                document_type="tri_party_agreement",
            )
        )
        LoanAccount.objects.filter(pk=account.pk).update(
            disbursed_amount="400000.00",
            principal_outstanding="300000.00",
            total_outstanding="300000.00",
            loan_account_status="partially_repaid",
        )
        login = self.client.post(
            "/api/v1/auth/login/",
            data={
                "email": "e2e.epic009.credit@sfpcl.example",
                "password": "ChecklistPass123!",
            },
            content_type="application/json",
        )
        self.assertEqual(login.status_code, 200, login.content)
        subsidiary = self.client.post(
            f"/api/v1/loan-accounts/{account.pk}/repayments/",
            data=json.dumps(
                {
                    "repayment_source": "subsidiary_deduction",
                    "amount_received": "75000.00",
                    "received_date": "2026-07-25",
                    "payment_method": "subsidiary_transfer",
                    "bank_reference_number": "SUB-CRITICAL-UAT-001",
                    "subsidiary_company_id": (
                        "00000000-0000-4000-8350-000000000001"
                    ),
                    "produce_payment_reference": "PRODUCE-CRITICAL-UAT-001",
                    "transfer_reference": "SUB-CRITICAL-UAT-001",
                    "remarks": "Deducted under the verified tri-party agreement.",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION=(
                f"Bearer {login.json()['data']['access_token']}"
            ),
            HTTP_IDEMPOTENCY_KEY="critical-uat-subsidiary-001",
        )
        self.assertEqual(subsidiary.status_code, 200, subsidiary.content)
        self.assertEqual(
            subsidiary.json()["data"]["reconciliation_status"],
            "pending_statement",
        )
        accounts_login = self.client.post(
            "/api/v1/auth/login/",
            data={
                "email": "e2e.uat.accounts@sfpcl.example",
                "password": "CriticalUat123!",
            },
            content_type="application/json",
        )
        self.assertEqual(accounts_login.status_code, 200, accounts_login.content)
        invoice = self.client.post(
            f"/api/v1/loan-accounts/{account.pk}/interest-invoices/",
            data=json.dumps({"financial_year": "FY2026-27"}),
            content_type="application/json",
            HTTP_AUTHORIZATION=(
                f"Bearer {accounts_login.json()['data']['access_token']}"
            ),
            HTTP_IDEMPOTENCY_KEY="critical-uat-interest-001",
        )
        self.assertEqual(invoice.status_code, 200, invoice.content)
        self.assertEqual(invoice.json()["data"]["financial_year"], "FY2026-27")
        self.assertTrue(
            all(
                status == ComplianceEvidence.REVIEW_ACCEPTED
                for status in ComplianceEvidence.objects.filter(
                    source_period="2026-Q2"
                ).values_list("review_status", flat=True)
            )
        )
