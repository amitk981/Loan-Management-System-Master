from django.test import Client, TestCase
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from contextlib import ExitStack
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.tests.api_contracts import assert_success_envelope
from sfpcl_credit.workflows.models import WorkflowEvent


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


class DisbursementReadinessApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_loan_account_creation_api import (
            LoanAccountCreationApiTests,
        )

        fixture = LoanAccountCreationApiTests(
            "test_terminal_sanction_creates_unfunded_account_terms_and_evidence"
        )
        fixture.setUp()
        self.fixture = fixture
        created = fixture._post(
            {
                "sanction_decision_id": str(fixture.sanction.pk),
                "loan_account_number": "LN-READINESS-001",
            }
        )
        self.assertEqual(created.status_code, 200, created.content)
        self.account_id = created.json()["data"]["loan_account_id"]
        self.application = fixture.application
        self.actor = fixture.actor
        self.actor.primary_role.role_code = "senior_manager_finance"
        self.actor.primary_role.save(update_fields=["role_code"])
        fixture._grant(self.actor, "finance.disbursement.readiness")
        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest

        SapCustomerProfileRequest.objects.create(
            loan_application=self.application,
            member=self.application.member,
            requested_by_user=self.actor,
            assigned_to_user=self.actor,
            farmer_full_name=self.application.member.legal_name,
            borrower_type=self.application.borrower_type,
            folio_number=self.application.member.folio_number,
            pan_number_encrypted="scope-only",
            address_text="scope-only",
            loan_application_number=self.application.application_reference_number,
            sanctioned_amount=self._account().sanctioned_amount,
            sanction_date=timezone.localdate(),
            excel_file=DocumentFile.objects.first(),
            sanction_decision_id_snapshot=self._account().sanction_decision_id,
            sanction_approval_case_id_snapshot=fixture.case.pk,
        )
        self.password = fixture.password
        self.client = Client()

    def test_incomplete_sources_return_every_ordered_safe_blocker_without_writes(self):
        auth = self._auth()
        before_audits = AuditLog.objects.count()
        before_workflows = WorkflowEvent.objects.count()

        response = self.client.get(
            f"/api/v1/loan-accounts/{self.account_id}/disbursement-readiness/",
            **auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        assert_success_envelope(self, response.json())
        data = response.json()["data"]
        self.assertEqual(data["loan_account_id"], self.account_id)
        self.assertEqual(
            data["loan_application_id"], str(self.application.pk)
        )
        self.assertFalse(data["ready_for_disbursement"])
        self.assertEqual([item["code"] for item in data["checks"]], CHECK_CODES)
        self.assertTrue(all(item["status"] in {"pass", "fail"} for item in data["checks"]))
        failed = [item for item in data["checks"] if item["status"] == "fail"]
        self.assertTrue(failed)
        self.assertTrue(all(item.get("reason") for item in failed))
        self.assertEqual(AuditLog.objects.count(), before_audits)
        self.assertEqual(WorkflowEvent.objects.count(), before_workflows)
        secret_surface = str(response.json())
        for forbidden in (
            "protected-pan",
            "protected-aadhaar",
            "account_number",
            "storage_key",
            "checksum",
            "capability",
            "CUST-",
        ):
            self.assertNotIn(forbidden, secret_surface)

    def test_all_current_owner_decisions_return_ready(self):
        from sfpcl_credit.sap_workflow.models import SapCustomerCode
        from sfpcl_credit.loans.models import LoanAccount

        code = SapCustomerCode.objects.create(
            member=self.application.member,
            sap_customer_code="CUST-READY-001",
            created_for_loan_application=self.application,
            created_by_user=self.actor,
            status="active",
        )
        LoanAccount.objects.filter(pk=self.account_id).update(sap_customer_code_id=code.pk)
        approval = SimpleNamespace(
            sanction_approved=True,
            exception_approval_complete=True,
            general_meeting_approval_complete=True,
            appraisal_complete=True,
        )
        legal = SimpleNamespace(
            documentation_complete=True,
            company_secretary_approval=True,
            credit_manager_approval=True,
            sanction_committee_approval=True,
            term_sheet_complete=True,
            loan_agreement_complete=True,
            signature_mismatch_resolved=True,
        )
        security = SimpleNamespace(
            security_package_complete=True,
            poa_complete=True,
            sh4_complete=True,
            cdsl_pledge_complete=True,
            blank_dated_cheque_received=True,
        )
        bank = SimpleNamespace(valid=True)
        sap = SimpleNamespace(
            customer_code_id=code.pk,
            member_id=self.application.member_id,
            loan_application_id=self.application.pk,
            status="active",
        )
        source_bank = SimpleNamespace(active=True)

        with (
            patch(
                "sfpcl_credit.disbursements.modules.disbursement_readiness."
                "resolve_approval_readiness",
                return_value=approval,
            ),
            patch(
                "sfpcl_credit.disbursements.modules.disbursement_readiness."
                "resolve_legal_readiness",
                return_value=legal,
            ),
            patch(
                "sfpcl_credit.disbursements.modules.disbursement_readiness."
                "resolve_security_readiness",
                return_value=security,
            ),
            patch(
                "sfpcl_credit.disbursements.modules.disbursement_readiness."
                "resolve_blank_cheque_bank_fact",
                return_value=bank,
            ),
            patch(
                "sfpcl_credit.disbursements.modules.disbursement_readiness."
                "resolve_sap_code",
                return_value=sap,
            ),
            patch(
                "sfpcl_credit.disbursements.modules.disbursement_readiness."
                "resolve_source_bank_account",
                return_value=source_bank,
            ),
        ):
            response = self.client.get(
                f"/api/v1/loan-accounts/{self.account_id}/disbursement-readiness/",
                **self._auth(),
            )

        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()["data"]
        self.assertTrue(data["ready_for_disbursement"])
        self.assertEqual([item["code"] for item in data["checks"]], CHECK_CODES)
        self.assertTrue(all(item["status"] == "pass" for item in data["checks"]))
        self.assertTrue(all("reason" not in item for item in data["checks"]))

    def test_each_source_fact_independently_blocks_aggregate_readiness(self):
        from sfpcl_credit.sap_workflow.models import SapCustomerCode
        from sfpcl_credit.loans.models import LoanAccount

        code = SapCustomerCode.objects.create(
            member=self.application.member,
            sap_customer_code="CUST-FLIP-001",
            created_for_loan_application=self.application,
            created_by_user=self.actor,
            status="active",
        )
        LoanAccount.objects.filter(pk=self.account_id).update(sap_customer_code_id=code.pk)
        account = SimpleNamespace(
            loan_account_id=self._account().pk,
            loan_application_id=self.application.pk,
            member_id=self.application.member_id,
            sanction_decision_id=self._account().sanction_decision_id,
            sap_customer_code_id=code.pk,
            loan_account_status="sanctioned",
            sanctioned_amount=Decimal("400000.00"),
            disbursement_amount=Decimal("400000.00"),
            member_kyc_status="verified",
            relationships_coherent=True,
        )
        owners = {
            "approval": SimpleNamespace(
                sanction_approved=True,
                exception_approval_complete=True,
                general_meeting_approval_complete=True,
                appraisal_complete=True,
            ),
            "legal": SimpleNamespace(
                documentation_complete=True,
                company_secretary_approval=True,
                credit_manager_approval=True,
                sanction_committee_approval=True,
                term_sheet_complete=True,
                loan_agreement_complete=True,
                signature_mismatch_resolved=True,
            ),
            "security": SimpleNamespace(
                security_package_complete=True,
                poa_complete=True,
                sh4_complete=True,
                cdsl_pledge_complete=True,
                blank_dated_cheque_received=True,
            ),
            "bank": SimpleNamespace(
                valid=True,
                cancelled_cheque_verified=True,
                bank_account_verified=True,
            ),
            "sap": SimpleNamespace(
                customer_code_id=code.pk,
                member_id=self.application.member_id,
                loan_application_id=self.application.pk,
                status="active",
            ),
            "source_bank": SimpleNamespace(active=True),
        }
        flips = {
            "sanction_approved": ("approval", "sanction_approved", False),
            "loan_account_sanctioned": ("account", "loan_account_status", "active"),
            "exception_approval_complete": ("approval", "exception_approval_complete", False),
            "general_meeting_approval_complete": ("approval", "general_meeting_approval_complete", False),
            "kyc_complete": ("account", "member_kyc_status", "pending"),
            "appraisal_complete": ("approval", "appraisal_complete", False),
            "documentation_complete": ("legal", "documentation_complete", False),
            "company_secretary_approval": ("legal", "company_secretary_approval", False),
            "credit_manager_approval": ("legal", "credit_manager_approval", False),
            "sanction_committee_approval": ("legal", "sanction_committee_approval", False),
            "security_package_complete": ("security", "security_package_complete", False),
            "poa_complete": ("security", "poa_complete", False),
            "term_sheet_complete": ("legal", "term_sheet_complete", False),
            "loan_agreement_complete": ("legal", "loan_agreement_complete", False),
            "sh4_complete": ("security", "sh4_complete", False),
            "cdsl_pledge_complete": ("security", "cdsl_pledge_complete", False),
            "blank_dated_cheque_received": ("security", "blank_dated_cheque_received", False),
            "cancelled_cheque_verified": ("bank", "cancelled_cheque_verified", False),
            "bank_account_verified": ("bank", "bank_account_verified", False),
            "signature_mismatch_resolved": ("legal", "signature_mismatch_resolved", False),
            "sap_customer_code_present": ("sap", "status", "inactive"),
            "source_bank_account_configured": ("source_bank", "active", False),
            "amount_within_sanction": ("account", "disbursement_amount", Decimal("400000.01")),
        }
        auth = self._auth()
        for expected_code, (owner, attribute, value) in flips.items():
            with self.subTest(expected_code=expected_code):
                current_account = SimpleNamespace(**vars(account))
                current = {
                    key: SimpleNamespace(**vars(facts)) for key, facts in owners.items()
                }
                target = current_account if owner == "account" else current[owner]
                setattr(target, attribute, value)
                with ExitStack() as stack:
                    for symbol, result in (
                        ("resolve_readiness_account", current_account),
                        ("resolve_approval_readiness", current["approval"]),
                        ("resolve_legal_readiness", current["legal"]),
                        ("resolve_security_readiness", current["security"]),
                        ("resolve_blank_cheque_bank_fact", current["bank"]),
                        ("resolve_sap_code", current["sap"]),
                        ("resolve_source_bank_account", current["source_bank"]),
                    ):
                        stack.enter_context(
                            patch(
                                "sfpcl_credit.disbursements.modules."
                                f"disbursement_readiness.{symbol}",
                                return_value=result,
                            )
                        )
                    response = self.client.get(
                        f"/api/v1/loan-accounts/{self.account_id}/disbursement-readiness/",
                        **auth,
                    )
                self.assertEqual(response.status_code, 200, response.content)
                data = response.json()["data"]
                self.assertFalse(data["ready_for_disbursement"])
                failed = [item["code"] for item in data["checks"] if item["status"] == "fail"]
                self.assertEqual(failed, [expected_code])

    def test_permission_role_scope_inactive_and_missing_ids_are_nondisclosing(self):
        wrong_role = self.fixture._user("credit_manager", "Wrong Role")
        self.fixture._grant(wrong_role, "finance.disbursement.readiness")
        missing_permission = self.fixture._user(
            "chief_financial_controller", "Missing Permission"
        )
        for actor in (wrong_role, missing_permission):
            with self.subTest(actor=actor.email):
                response = self.client.get(
                    f"/api/v1/loan-accounts/{self.account_id}/disbursement-readiness/",
                    **self._auth_for(actor),
                )
                self.assertEqual(response.status_code, 403, response.content)
                self.assertEqual(response.json()["error"]["code"], "FORBIDDEN")

        self.fixture._grant(missing_permission, "finance.disbursement.readiness")
        cfc_stage_scope = self.client.get(
            f"/api/v1/loan-accounts/{self.account_id}/disbursement-readiness/",
            **self._auth_for(missing_permission),
        )
        self.assertEqual(cfc_stage_scope.status_code, 403, cfc_stage_scope.content)
        self.assertEqual(cfc_stage_scope.json()["error"]["code"], "OBJECT_ACCESS_DENIED")

        missing = self.client.get(
            f"/api/v1/loan-accounts/{uuid4()}/disbursement-readiness/",
            **self._auth(),
        )
        self.assertEqual(missing.status_code, 403, missing.content)
        self.assertEqual(missing.json()["error"]["code"], "OBJECT_ACCESS_DENIED")

        headers = self._auth()
        self.actor.status = "inactive"
        self.actor.save(update_fields=["status"])
        inactive = self.client.get(
            f"/api/v1/loan-accounts/{self.account_id}/disbursement-readiness/",
            **headers,
        )
        self.assertEqual(inactive.status_code, 401, inactive.content)

    def test_cfc_exact_scope_and_unknown_query_contract(self):
        cfc = self.fixture._user("chief_financial_controller", "CFC")
        self.fixture._grant(cfc, "finance.disbursement.readiness")
        unrelated = self.fixture._user("field_officer", "Unrelated Intake Owner")
        self.application.received_by_user = unrelated
        self.application.save(update_fields=["received_by_user"])
        permitted = self.client.get(
            f"/api/v1/loan-accounts/{self.account_id}/disbursement-readiness/",
            **self._auth_for(cfc),
        )
        self.assertEqual(permitted.status_code, 403, permitted.content)
        self.assertEqual(permitted.json()["error"]["code"], "OBJECT_ACCESS_DENIED")

        unknown = self.client.get(
            f"/api/v1/loan-accounts/{self.account_id}/disbursement-readiness/?page=1",
            **self._auth_for(cfc),
        )
        self.assertEqual(unknown.status_code, 400, unknown.content)
        self.assertEqual(unknown.json()["error"]["code"], "VALIDATION_ERROR")
        self.assertEqual(
            unknown.json()["error"]["field_errors"],
            {"page": "Unknown query parameter."},
        )

    def test_senior_finance_scope_ignores_application_origination_assignment(self):
        unrelated = self.fixture._user("field_officer", "Different Intake Assignee")
        self.application.received_by_user = unrelated
        self.application.save(update_fields=["received_by_user"])

        response = self.client.get(
            f"/api/v1/loan-accounts/{self.account_id}/disbursement-readiness/",
            **self._auth(),
        )

        self.assertEqual(response.status_code, 200, response.content)

    def test_cross_member_account_and_sap_scope_fail_nondisclosing(self):
        from sfpcl_credit.members.models import Member
        from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest

        unrelated = Member.objects.create(
            member_number="READINESS-UNRELATED-MEMBER",
            member_type="individual_farmer",
            legal_name="Unrelated Readiness Member",
            display_name="Unrelated Readiness Member",
            folio_number="READINESS-UNRELATED-FOLIO",
            membership_status="active",
            kyc_status="verified",
            default_status="no_default",
        )
        account = self._account()
        account.member = unrelated
        account.save(update_fields=["member"])
        denied = self.client.get(
            f"/api/v1/loan-accounts/{self.account_id}/disbursement-readiness/",
            **self._auth(),
        )
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(denied.json()["error"]["code"], "OBJECT_ACCESS_DENIED")

        account.member = self.application.member
        account.save(update_fields=["member"])
        request = SapCustomerProfileRequest.objects.get(
            loan_application=self.application
        )
        request.member = unrelated
        request.save(update_fields=["member"])
        denied = self.client.get(
            f"/api/v1/loan-accounts/{self.account_id}/disbursement-readiness/",
            **self._auth(),
        )
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(denied.json()["error"]["code"], "OBJECT_ACCESS_DENIED")

    def test_real_projection_is_query_bounded(self):
        auth = self._auth()
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                f"/api/v1/loan-accounts/{self.account_id}/disbursement-readiness/",
                **auth,
            )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertLessEqual(len(queries), 30)

    def test_stale_application_lifecycle_fails_the_sanction_check(self):
        from sfpcl_credit.applications.models import LoanApplication

        LoanApplication.objects.filter(pk=self.application.pk).update(
            application_status=LoanApplication.STATUS_REJECTED_BY_SANCTION
        )
        response = self.client.get(
            f"/api/v1/loan-accounts/{self.account_id}/disbursement-readiness/",
            **self._auth(),
        )
        self.assertEqual(response.status_code, 200, response.content)
        statuses = {
            item["code"]: item["status"] for item in response.json()["data"]["checks"]
        }
        self.assertEqual(statuses["sanction_approved"], "fail")

    def test_mutable_security_package_status_cannot_replace_terminal_evidence(self):
        from sfpcl_credit.security_instruments.models import SecurityPackage

        SecurityPackage.objects.create(
            loan_application=self.application,
            physical_share_security_required_flag=False,
            demat_pledge_required_flag=False,
            poa_required_flag=True,
            blank_cheque_required_flag=False,
            cancelled_cheque_required_flag=False,
            security_status=SecurityPackage.STATUS_COMPLETE,
        )

        response = self.client.get(
            f"/api/v1/loan-accounts/{self.account_id}/disbursement-readiness/",
            **self._auth(),
        )

        self.assertEqual(response.status_code, 200, response.content)
        statuses = {
            item["code"]: item["status"] for item in response.json()["data"]["checks"]
        }
        self.assertEqual(statuses["security_package_complete"], "fail")

    def _account(self):
        from sfpcl_credit.loans.models import LoanAccount

        return LoanAccount.objects.get(pk=self.account_id)

    def _auth(self):
        return self._auth_for(self.actor)

    def _auth_for(self, actor):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": actor.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {
            "HTTP_AUTHORIZATION": f"Bearer {response.json()['data']['access_token']}"
        }
