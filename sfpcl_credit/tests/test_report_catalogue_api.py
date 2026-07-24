import json
from datetime import date
from uuid import uuid4

from django.db import connection
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from sfpcl_credit.identity.models import Role, User
from sfpcl_credit.tests.api_contracts import assert_pagination_shape


def get_with_query_bound(test_case, client, path, auth, maximum=40):
    with CaptureQueriesContext(connection) as queries:
        response = client.get(path, **auth)
    test_case.assertLessEqual(
        len(queries),
        maximum,
        f"Report query count exceeded {maximum}: {path}",
    )
    return response


def assert_validation_error(test_case, response, field):
    test_case.assertEqual(response.status_code, 400, response.content)
    test_case.assertEqual(response.json()["error"]["code"], "VALIDATION_ERROR")
    test_case.assertIn(field, response.json()["error"]["field_errors"])


class ReportCatalogueApiTests(TestCase):
    password = "ReportCataloguePass123!"

    def setUp(self):
        self.client = Client()
        role = Role.objects.create(
            role_code="report_catalogue_no_access",
            role_name="Report Catalogue No Access",
        )
        self.actor = User.objects.create(
            full_name="Report Catalogue No Access",
            email="report.catalogue.no.access@sfpcl.example",
            primary_role=role,
            password_hash="",
        )
        self.actor.set_password(self.password)
        self.actor.save(update_fields=["password_hash"])

    def test_all_required_catalogue_codes_are_registered_and_default_deny(self):
        auth = self._auth()

        for report_code in (
            "credit-sanction",
            "exception",
            "security-custody",
            "sap-pending",
            "disbursement",
            "repayment",
            "interest-invoice",
            "interest-accrual",
            "cfo-quarterly-mis",
            "default",
            "recovery",
            "closure-noc",
            "section-186",
            "nbfc-test",
            "kyc-rekyc",
            "stamp-duty",
            "money-lending-review",
            "grievance",
            "audit-log-export",
        ):
            with self.subTest(report_code=report_code):
                response = self.client.get(
                    f"/api/v1/reports/{report_code}/",
                    **auth,
                )

                self.assertEqual(response.status_code, 403, response.content)
                self.assertEqual(response.json()["error"]["code"], "FORBIDDEN")
                self.assertNotIn("data", response.json())
                self.assertNotIn("pagination", response.json())

    def test_complete_catalogue_has_23_product_reports_and_two_fixed_section_40_apis(self):
        from sfpcl_credit.reports.registry import REPORTS

        self.assertEqual(len(REPORTS), 25)
        self.assertEqual(
            REPORTS["audit-log-export"].restricted_handoff,
            "012C-sensitive-export-policy+012D-audit-selector",
        )
        self.assertIsNotNone(REPORTS["audit-log-export"].selector)

    def test_audit_export_handoff_cannot_query_even_with_read_and_export_permissions(self):
        from sfpcl_credit.identity.models import Permission, RolePermission

        for code in (
            "audit.audit_log.read",
            "audit.export",
            "reports.export",
            "reports.export_sensitive",
        ):
            permission = Permission.objects.create(
                permission_code=code,
                permission_name=code,
                module_name="audit",
                risk_level="critical",
            )
            RolePermission.objects.create(
                role=self.actor.primary_role,
                permission=permission,
            )

        response = self.client.get(
            "/api/v1/reports/audit-log-export/",
            **self._auth(),
        )

        self.assertEqual(response.status_code, 403, response.content)
        self.assertEqual(response.json()["error"]["code"], "FORBIDDEN")
        self.assertNotIn("data", response.json())

    def _auth(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": self.actor.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {
            "HTTP_AUTHORIZATION": (
                f"Bearer {response.json()['data']['access_token']}"
            )
        }


class DefaultReportCatalogueApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_default_case_opening_api import (
            DefaultCaseOpeningApiTests,
        )

        fixture = DefaultCaseOpeningApiTests(
            "test_scoped_detail_and_filtered_list_return_the_same_case_contract"
        )
        fixture.setUp()
        self.fixture = fixture
        self.client = Client()

    def test_default_report_reconciles_scoped_owner_projection_and_filters(self):
        from sfpcl_credit.loans.models import RepaymentSchedule

        due_date = date(2026, 6, 22)
        RepaymentSchedule.objects.create(
            loan_account=self.fixture.account,
            installment_number=1,
            due_date=due_date,
            principal_due="1000.00",
            interest_due="0.00",
            charges_due="0.00",
            total_due="1000.00",
            schedule_status="pending",
        )
        opened = self.client.post(
            (
                f"/api/v1/loan-accounts/{self.fixture.account.pk}/"
                "default-cases/open/"
            ),
            data=json.dumps(
                {
                    "trigger_event": "missed_principal_repayment",
                    "scheduled_due_date": due_date.isoformat(),
                    "reason": "Missed principal.",
                }
            ),
            content_type="application/json",
            **self.fixture.auth,
        )
        self.assertEqual(opened.status_code, 200, opened.content)

        owner = self.client.get(
            (
                "/api/v1/default-cases/?"
                "default_case_status=grace_period_active"
                f"&loan_account_id={self.fixture.account.pk}"
            ),
            **self.fixture.auth,
        )
        report = get_with_query_bound(
            self,
            self.client,
            (
                "/api/v1/reports/default/?"
                "default_case_status=grace_period_active"
                f"&loan_account_id={self.fixture.account.pk}"
            ),
            self.fixture.auth,
        )

        self.assertEqual(owner.status_code, 200, owner.content)
        self.assertEqual(report.status_code, 200, report.content)
        self.assertEqual(report.json()["data"], owner.json()["data"])
        self.assertEqual(
            report.json()["pagination"]["total_count"],
            owner.json()["pagination"]["total_count"],
        )
        self.assertEqual(
            report.json()["data"][0]["default_case_id"],
            opened.json()["data"]["default_case_id"],
        )
        self.assertNotIn("evidence_document_ids", str(report.json()))
        assert_validation_error(
            self,
            self.client.get(
                "/api/v1/reports/default/?default_case_status=unknown",
                **self.fixture.auth,
            ),
            "default_case_status",
        )


class RecoveryReportCatalogueApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_recovery_action_api import RecoveryActionApiTests

        fixture = RecoveryActionApiTests(
            "test_company_secretary_initiates_exact_approved_sh4_with_governed_evidence"
        )
        fixture.setUp()
        self.fixture = fixture
        self.client = fixture.client

    def test_recovery_report_reconciles_approved_decision_without_restricted_evidence(self):
        decision, _case = self.fixture._approved_decision()
        _actor, auth = self.fixture._executor()

        report = get_with_query_bound(
            self,
            self.client,
            "/api/v1/reports/recovery/?decision=invoke_sh4",
            auth,
        )

        self.assertEqual(report.status_code, 200, report.content)
        self.assertEqual(report.json()["pagination"]["total_count"], 1)
        row = report.json()["data"][0]
        self.assertEqual(
            row["recovery_decision_id"],
            decision["recovery_decision_id"],
        )
        self.assertEqual(row["decision"], "invoke_sh4")
        self.assertNotIn("approval_evidence", str(report.json()))
        self.assertNotIn("document_ids", str(report.json()))
        self.assertNotIn("interaction_log", str(report.json()))
        assert_validation_error(
            self,
            self.client.get(
                "/api/v1/reports/recovery/?decision=unknown",
                **auth,
            ),
            "decision",
        )


class StatutoryReportCatalogueApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_statutory_trackers import (
            StatutoryTrackerModuleTests,
        )

        fixture = StatutoryTrackerModuleTests(
            "test_section_186_calculate_uses_higher_limit_and_flags_excess"
        )
        fixture.setUp()
        self.fixture = fixture
        self.client = Client()
        fixture.client = self.client

    def test_section_186_and_nbfc_reports_reconcile_owner_calculations(self):
        from sfpcl_credit.compliance.modules.nbfc_principal_business_test import (
            NbfcPrincipalBusinessTestModule,
        )
        from sfpcl_credit.compliance.modules.section186_tracker import (
            Section186TrackerModule,
        )

        for permission in (
            "compliance.section186.read",
            "compliance.nbfc_test.create",
            "compliance.nbfc_test.read",
        ):
            self.fixture._grant(self.fixture.cfo_role, permission)
        section_task, section_evidence = self.fixture._accepted_evidence(
            "SECTION_186_LIMIT"
        )
        section = Section186TrackerModule.calculate(
            actor=self.fixture.cfo,
            period_id=section_task.pk,
            payload={
                "financial_year": "FY2026-27",
                "quarter": "Q1",
                "paid_up_capital_amount": "100.00",
                "free_reserves_amount": "100.00",
                "securities_premium_amount": "0.00",
                "total_loans_exposure_amount": "100.00",
                "compliance_evidence_id": str(section_evidence.pk),
            },
        )
        nbfc_task, nbfc_evidence = self.fixture._accepted_evidence(
            "NBFC_PRINCIPAL_TEST"
        )
        nbfc = NbfcPrincipalBusinessTestModule.calculate(
            actor=self.fixture.cfo,
            period_id=nbfc_task.pk,
            payload={
                "financial_year": "FY2026-27",
                "quarter": "Q1",
                "financial_assets_amount": "51.00",
                "total_assets_amount": "100.00",
                "financial_income_amount": "51.00",
                "gross_income_amount": "100.00",
                "early_warning_threshold_ratio": "40.0000",
                "compliance_evidence_id": str(nbfc_evidence.pk),
            },
        )
        auth = self.fixture._auth(self.fixture.cfo)

        section_report = self.client.get(
            "/api/v1/reports/section-186/?financial_year=FY2026-27&quarter=Q1",
            **auth,
        )
        nbfc_report = self.client.get(
            "/api/v1/reports/nbfc-test/?financial_year=FY2026-27&quarter=Q1",
            **auth,
        )

        self.assertEqual(section_report.status_code, 200, section_report.content)
        self.assertEqual(nbfc_report.status_code, 200, nbfc_report.content)
        self.assertEqual(
            section_report.json()["data"][0]["section_186_tracker_id"],
            str(section.pk),
        )
        self.assertEqual(
            nbfc_report.json()["data"][0]["nbfc_principal_test_id"],
            str(nbfc.pk),
        )
        self.assertEqual(
            section_report.json()["pagination"]["totals"],
            {
                "applicable_limit_amount": "120.00",
                "total_loans_exposure_amount": "100.00",
            },
        )
        self.assertTrue(
            nbfc_report.json()["data"][0]["registration_triggered_flag"]
        )
        assert_validation_error(
            self,
            self.client.get(
                "/api/v1/reports/section-186/?quarter=Q5",
                **auth,
            ),
            "quarter",
        )


class KycReportCatalogueApiTests(TestCase):
    def test_kyc_report_reuses_scoped_masked_owner_summary(self):
        from sfpcl_credit.compliance.models import KYCReview
        from sfpcl_credit.identity.models import Permission, RolePermission
        from sfpcl_credit.members.models import MemberScopeAssignment
        from sfpcl_credit.tests.test_kyc_review_tracker import KycReviewTrackerTests

        fixture = KycReviewTrackerTests(
            "test_last_completed_individual_kyc_generates_one_two_year_warning_review_and_task"
        )
        fixture.setUp()
        fixture.test_last_completed_individual_kyc_generates_one_two_year_warning_review_and_task()
        fixture.owner.set_password("KycReportPass123!")
        fixture.owner.save(update_fields=["password_hash"])
        permission = Permission.objects.create(
            permission_code="compliance.kyc_review.manage",
            permission_name="Manage KYC reviews",
            module_name="compliance",
            risk_level="high",
        )
        RolePermission.objects.create(role=fixture.owner_role, permission=permission)
        review = KYCReview.objects.get()
        MemberScopeAssignment.objects.create(
            user=fixture.owner,
            permission_code=permission.permission_code,
            scope_type="assigned",
            member=review.member,
        )
        login = self.client.post(
            "/api/v1/auth/login/",
            {"email": fixture.owner.email, "password": "KycReportPass123!"},
            content_type="application/json",
        )
        auth = {
            "HTTP_AUTHORIZATION": (
                f"Bearer {login.json()['data']['access_token']}"
            )
        }

        response = self.client.get(
            "/api/v1/reports/kyc-rekyc/?status=warning",
            **auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            response.json()["data"][0]["kyc_review_id"],
            str(review.pk),
        )
        self.assertNotIn("pan_encrypted", str(response.json()))
        self.assertNotIn("encrypted-pan", str(response.json()))
        self.assertNotIn("document_id", str(response.json()))


class GrievanceReportCatalogueApiTests(TestCase):
    def test_grievance_report_reuses_scoped_owner_rows_without_internal_narrative(self):
        from sfpcl_credit.tests.test_grievance_workflow import (
            GrievanceWorkflowApiTests,
        )

        fixture = GrievanceWorkflowApiTests(
            "test_staff_reads_are_member_scoped_and_borrower_projection_is_safe"
        )
        fixture.setUp()
        own = fixture._grievance(
            "GRV-2026-REPORT000001",
            loan_application=fixture.application,
            grievance_category="application_issue",
            description="Scoped report complaint.",
            received_channel="form",
            internal_notes="Restricted investigation narrative.",
        )

        response = fixture.client.get(
            "/api/v1/reports/grievance/?status=open",
            **fixture._auth(fixture.company_secretary),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 1)
        self.assertEqual(response.json()["data"][0]["grievance_id"], str(own.pk))
        self.assertNotIn("internal_notes", str(response.json()))
        self.assertNotIn("history", str(response.json()))


class ClosureReportCatalogueApiTests(TestCase):
    def test_closure_report_reconciles_owner_close_without_document_authority(self):
        from sfpcl_credit.tests.test_closure_api import LoanClosureApiTests

        fixture = LoanClosureApiTests(
            "test_full_repayment_close_freezes_fresh_facts_and_creates_controlled_requirements"
        )
        fixture.setUp()
        closed = fixture._close(idempotency_key="closure-report-001")
        self.assertEqual(closed.status_code, 200, closed.content)

        response = fixture.client.get(
            "/api/v1/reports/closure-noc/?closure_stage=financially_closed",
            **fixture.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 1)
        self.assertEqual(
            response.json()["data"][0]["loan_closure_id"],
            closed.json()["data"]["loan_closure_id"],
        )
        self.assertNotIn("document_id", str(response.json()))
        self.assertNotIn("file_location", str(response.json()))


class MoneyLendingReportCatalogueApiTests(TestCase):
    def test_money_lending_report_reconciles_review_without_restricted_documents(self):
        from sfpcl_credit.compliance.models import MoneyLendingLawReview
        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.tests.test_global_search_compliance import (
            GlobalSearchComplianceTests,
        )

        fixture = GlobalSearchComplianceTests(
            "test_governed_evidence_and_money_lending_review_are_minimised"
        )
        fixture.setUp()
        fixture._grant("compliance.money_lending_review.manage")
        task, evidence = fixture._accepted_evidence(
            "MONEY_LENDING_ANNUAL",
            "Annual money-lending compliance",
            period="FY2026-27",
        )
        board_note = DocumentFile.objects.create(
            file_name="restricted-board-note.pdf",
            storage_provider="test",
            storage_key="tests/restricted-board-note.pdf",
            sensitivity_level=DocumentFile.SENSITIVITY_RESTRICTED,
            uploaded_by_user=fixture.owner,
        )
        review = MoneyLendingLawReview.objects.create(
            financial_year="FY2026-27",
            state="Maharashtra",
            applicability="exempt",
            exemption_applicable_flag=True,
            legal_opinion_document=evidence.document,
            board_note_document=board_note,
            task=task,
            evidence=evidence,
            reviewed_by_user=fixture.owner,
            remarks="Restricted opinion narrative.",
        )
        login = fixture.client.post(
            "/api/v1/auth/login/",
            {"email": fixture.owner.email, "password": fixture.PASSWORD},
            content_type="application/json",
        )
        auth = {
            "HTTP_AUTHORIZATION": (
                f"Bearer {login.json()['data']['access_token']}"
            )
        }

        response = fixture.client.get(
            "/api/v1/reports/money-lending-review/?financial_year=FY2026-27",
            **auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            response.json()["data"][0]["money_lending_law_review_id"],
            str(review.pk),
        )
        self.assertNotIn("document_id", str(response.json()))
        self.assertNotIn("narrative", str(response.json()))


class DisbursementReportCatalogueApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_disbursement_initiation_api import (
            DisbursementInitiationApiTests,
        )

        fixture = DisbursementInitiationApiTests(
            "test_current_ready_payment_is_recorded_once_without_transfer_side_effects"
        )
        fixture.setUp()
        fixture.client = Client()
        self.fixture = fixture
        self.client = fixture.client
        self.reader = fixture.cfc
        fixture.fixture._grant(
            self.reader,
            "finance.disbursement.readiness",
            "finance.loan_account.read",
        )

    def test_full_disbursement_report_reconciles_amount_reference_status_date_and_total(self):
        initiated = self.fixture._post(key="catalogue-disbursement-initiation")
        self.assertEqual(initiated.status_code, 200, initiated.content)

        response = get_with_query_bound(
            self,
            self.client,
            (
                "/api/v1/reports/disbursement/"
                "?bank_transfer_status=pending&page=1&page_size=10"
            ),
            self.fixture._auth(self.reader),
        )

        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        assert_pagination_shape(self, body)
        self.assertEqual(body["pagination"]["total_count"], 1)
        self.assertEqual(
            body["pagination"]["totals"],
            {"disbursement_amount": "400000.00"},
        )
        row = body["data"][0]
        self.assertEqual(row["disbursement_amount"], "400000.00")
        self.assertEqual(row["bank_reference_number"], None)
        self.assertEqual(row["bank_transfer_status"], "pending")
        self.assertEqual(row["disbursed_at"], None)
        self.assertEqual(
            row["loan_account_id"],
            str(self.fixture.account_id),
        )
        assert_validation_error(
            self,
            self.client.get(
                "/api/v1/reports/disbursement/?bank_transfer_status=unknown",
                **self.fixture._auth(self.reader),
            ),
            "bank_transfer_status",
        )


class RepaymentReportCatalogueApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_direct_repayment_posting_api import (
            DirectRepaymentPostingApiTests,
        )

        fixture = DirectRepaymentPostingApiTests(
            "test_valid_direct_receipt_and_exact_replay_create_one_pending_obligation"
        )
        fixture.setUp()
        self.fixture = fixture
        self.client = fixture.client

    def test_repayment_report_reconciles_receipt_filters_and_total(self):
        created = self.fixture._capture(
            {
                "repayment_source": "direct_farmer",
                "amount_received": "100000.00",
                "received_date": "2026-12-01",
                "payment_method": "neft",
                "bank_reference_number": "UTR-REPORT-001",
                "remarks": "Confirmed against the bank statement.",
            },
            "repayment-report-001",
        )
        self.assertEqual(created.status_code, 200, created.content)

        response = get_with_query_bound(
            self,
            self.client,
            (
                "/api/v1/reports/repayment/"
                "?from_date=2026-12-01&to_date=2026-12-01"
                "&repayment_source=direct_farmer"
            ),
            self.fixture.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        assert_pagination_shape(self, body)
        self.assertEqual(body["pagination"]["total_count"], 1)
        self.assertEqual(
            body["pagination"]["totals"],
            {"amount_received": "100000.00"},
        )
        self.assertEqual(
            body["data"][0],
            {
                "repayment_id": created.json()["data"]["repayment_id"],
                "loan_account_id": str(self.fixture.account.pk),
                "loan_account_number": self.fixture.account.loan_account_number,
                "member_id": str(self.fixture.account.member_id),
                "borrower_name": self.fixture.account.member.display_name,
                "repayment_source": "direct_farmer",
                "amount_received": "100000.00",
                "received_date": "2026-12-01",
                "payment_method": "neft",
                "bank_reference_number": "UTR-REPORT-001",
                "allocation_status": "pending",
                "sap_posting_status": "pending",
            },
        )
        assert_validation_error(
            self,
            self.client.get(
                "/api/v1/reports/repayment/?repayment_source=unknown",
                **self.fixture.auth,
            ),
            "repayment_source",
        )


class InterestInvoiceReportCatalogueApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_interest_invoice_api import (
            InterestInvoiceApiTests,
        )

        fixture = InterestInvoiceApiTests(
            "test_generation_uses_server_owned_fy_truth_and_leaves_balances_unchanged"
        )
        fixture.setUp()
        self.fixture = fixture
        self.client = fixture.client

    def test_interest_invoice_report_reuses_owner_projection_and_filters(self):
        created = self.fixture._generate("invoice-report-001")
        self.assertEqual(created.status_code, 200, created.content)

        response = get_with_query_bound(
            self,
            self.client,
            (
                "/api/v1/reports/interest-invoice/"
                "?financial_year=FY2026-27&invoice_status=draft"
            ),
            self.fixture.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        assert_pagination_shape(self, body)
        self.assertEqual(body["pagination"]["total_count"], 1)
        self.assertEqual(
            body["data"][0],
            created.json()["data"],
        )
        assert_validation_error(
            self,
            self.client.get(
                "/api/v1/reports/interest-invoice/?financial_year=2026-27",
                **self.fixture.auth,
            ),
            "financial_year",
        )


class InterestAccrualReportCatalogueApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_interest_accrual_api import (
            MonthlyInterestAccrualApiTests,
        )

        fixture = MonthlyInterestAccrualApiTests(
            "test_single_month_uses_server_owned_snapshots_and_creates_pending_sap_obligation"
        )
        fixture.setUp()
        self.fixture = fixture
        self.client = fixture.client

    def test_interest_accrual_report_reuses_owner_projection_filters_and_total(self):
        created = self.fixture._create("accrual-report-001")
        self.assertEqual(created.status_code, 200, created.content)

        response = get_with_query_bound(
            self,
            self.client,
            (
                "/api/v1/reports/interest-accrual/"
                "?accrual_month=2026-07&sap_posting_status=pending"
            ),
            self.fixture.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        assert_pagination_shape(self, body)
        self.assertEqual(body["pagination"]["total_count"], 1)
        self.assertEqual(
            body["pagination"]["totals"],
            {"interest_accrued_amount": "3142.47"},
        )
        self.assertEqual(body["data"][0], created.json()["data"])
        assert_validation_error(
            self,
            self.client.get(
                "/api/v1/reports/interest-accrual/?accrual_month=2026-13",
                **self.fixture.auth,
            ),
            "accrual_month",
        )


class CfoQuarterlyMisReportCatalogueApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_quarterly_mis_api import QuarterlyMisApiTests

        fixture = QuarterlyMisApiTests(
            "test_generate_freezes_cutoff_totals_and_exact_replay"
        )
        fixture.setUp()
        self.fixture = fixture
        self.client = fixture.client

    def test_cfo_quarterly_mis_report_reuses_frozen_owner_projection(self):
        from sfpcl_credit.loans.models import RepaymentSchedule

        RepaymentSchedule.objects.create(
            loan_account=self.fixture.account,
            installment_number=1,
            due_date=date(2025, 6, 29),
            principal_due="1000.00",
            interest_due="100.00",
            charges_due="0.00",
            total_due="1100.00",
            schedule_status="pending",
        )
        dpd = self.client.post(
            (
                f"/api/v1/loan-accounts/{self.fixture.account.pk}/"
                "dpd-status/calculate/"
            ),
            data='{"as_of_date":"2026-06-30"}',
            content_type="application/json",
            **self.fixture.auth,
        )
        self.assertEqual(dpd.status_code, 200, dpd.content)
        generated = self.fixture._generate()
        self.assertEqual(generated.status_code, 200, generated.content)

        response = get_with_query_bound(
            self,
            self.client,
            (
                "/api/v1/reports/cfo-quarterly-mis/"
                "?financial_year=FY2026-27&quarter=Q1"
            ),
            self.fixture.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        assert_pagination_shape(self, body)
        self.assertEqual(body["pagination"]["total_count"], 1)
        self.assertEqual(body["data"][0], generated.json()["data"])
        assert_validation_error(
            self,
            self.client.get(
                (
                    "/api/v1/reports/cfo-quarterly-mis/"
                    "?financial_year=FY2026-27&quarter=Q5"
                ),
                **self.fixture.auth,
            ),
            "filters",
        )


class SapPendingReportCatalogueApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_sap_customer_profile_request_api import (
            SapCustomerProfileRequestApiTests,
        )

        self.fixture = SapCustomerProfileRequestApiTests(
            "test_credit_manager_creates_draft_request_after_terminal_sanction"
        )
        self.fixture.setUp()
        self.client = Client()

    def tearDown(self):
        self.fixture.tearDown()

    def test_sap_pending_report_reuses_exact_assignee_workspace_and_masked_projection(self):
        request_id = self.fixture._create_and_send("sap-pending-report-001")

        response = get_with_query_bound(
            self,
            self.client,
            "/api/v1/reports/sap-pending/?request_status=sent",
            self.fixture._auth(self.fixture.assignee),
        )

        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        assert_pagination_shape(self, body)
        self.assertEqual(body["pagination"]["total_count"], 1)
        row = body["data"][0]
        self.assertEqual(row["request_id"], request_id)
        self.assertEqual(row["request_status"], "sent")
        self.assertEqual(row["customer_code_masked"], None)
        self.assertNotIn("aadhaar", str(row).lower())
        self.assertNotIn("pan_number", str(row).lower())
        assert_validation_error(
            self,
            self.client.get(
                "/api/v1/reports/sap-pending/?request_status=completed",
                **self.fixture._auth(self.fixture.assignee),
            ),
            "request_status",
        )


class SecurityCustodyReportCatalogueApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_sh4_api import SH4ApiTests

        fixture = SH4ApiTests(
            "test_distinct_company_secretary_records_terminal_custody_from_exact_legal_evidence"
        )
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fixture = fixture
        self.client = fixture.client

    def test_security_custody_report_reconciles_scoped_public_custody_truth(self):
        from sfpcl_credit.security_instruments.models import (
            SH4ShareTransferForm,
            SecurityPackage,
        )

        package_data = self.fixture._refresh_package()
        package = SecurityPackage.objects.get(
            pk=package_data["security_package_id"]
        )
        document, _stamp, _signatures = self.fixture.fixture._poa_evidence("sh4")
        custodian = self.fixture.fixture._user(
            "company_secretary",
            "security.package.read",
        )
        form = SH4ShareTransferForm.objects.create(
            security_package=package,
            member=self.fixture.member,
            witness=self.fixture.witness,
            shareholding=self.fixture.borrower_shareholding,
            share_count=75,
            loan_document=document,
            form_status=SH4ShareTransferForm.STATUS_HELD_IN_CUSTODY,
            custody_location="CS custody cabinet A-14",
            signed_at=timezone.localdate(),
            prepared_by_user=self.fixture.compliance,
            custodian_user=custodian,
            custody_evidence_json={"restricted": "must not be reported"},
            custody_workflow_event_id=uuid4(),
        )

        response = get_with_query_bound(
            self,
            self.client,
            "/api/v1/reports/security-custody/?instrument_type=sh4",
            self.fixture.fixture._auth(custodian),
        )

        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        assert_pagination_shape(self, body)
        self.assertEqual(body["pagination"]["total_count"], 1)
        self.assertEqual(
            body["data"][0],
            {
                "instrument_type": "sh4",
                "instrument_id": str(form.pk),
                "security_package_id": str(package.pk),
                "loan_application_id": str(self.fixture.application.pk),
                "loan_account_id": None,
                "member_id": str(self.fixture.member.pk),
                "custody_status": "held_in_custody",
                "custody_location": "CS custody cabinet A-14",
                "custody_recorded_at": form.updated_at.isoformat().replace(
                    "+00:00",
                    "Z",
                ),
            },
        )
        self.assertNotIn("restricted", str(body))
        self.assertNotIn("custodian_user_id", str(body))
        assert_validation_error(
            self,
            self.client.get(
                "/api/v1/reports/security-custody/?instrument_type=unknown",
                **self.fixture.fixture._auth(custodian),
            ),
            "instrument_type",
        )

class StampDutyReportCatalogueApiTests(TestCase):
    def test_stamp_duty_report_reuses_scoped_legal_record_without_evidence_file(self):
        from sfpcl_credit.legal_documents.models import StampDutyRecord
        from sfpcl_credit.tests.test_stamp_notary_api import (
            StampDutyAndNotarisationApiTests,
        )

        fixture = StampDutyAndNotarisationApiTests(
            "test_compliance_records_pending_stamp_with_atomic_status_and_evidence"
        )
        fixture.setUp()
        fixture.test_compliance_records_pending_stamp_with_atomic_status_and_evidence()
        stamp = StampDutyRecord.objects.get(
            loan_document=fixture.loan_document
        )

        response = fixture.client.get(
            "/api/v1/reports/stamp-duty/?status=pending",
            **fixture._auth(fixture.actor),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 1)
        self.assertEqual(
            response.json()["data"][0]["stamp_duty_record_id"],
            str(stamp.pk),
        )
        self.assertNotIn("evidence_document", str(response.json()))
        self.assertNotIn("remarks", str(response.json()))


class ApprovalReportCatalogueApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.approvals.models import (
            CreditSanctionRegisterEntry,
            ExceptionRegisterEntry,
        )
        from sfpcl_credit.tests.test_approval_case_routing_api import (
            ApprovalCaseRoutingApiTests,
        )
        from sfpcl_credit.workflows.models import WorkflowEvent

        fixture = ApprovalCaseRoutingApiTests(
            "test_exception_register_is_read_only_filtered_paginated_and_object_scoped"
        )
        fixture._build_fixture(fixture)
        fixture.client = Client()
        self.fixture = fixture
        self.client = fixture.client
        sanction_permission = fixture._permission(
            "approvals.sanction_register.read"
        )
        exception_permission = fixture._permission(
            "approvals.exception_register.read"
        )
        from sfpcl_credit.identity.models import RolePermission

        RolePermission.objects.create(
            role=fixture.cfo.primary_role,
            permission=sanction_permission,
        )
        RolePermission.objects.create(
            role=fixture.cfo.primary_role,
            permission=exception_permission,
        )
        workflow = WorkflowEvent.objects.create(
            workflow_name="credit_sanction",
            entity_type="approval_case",
            entity_id=fixture.case.pk,
            from_state="pending",
            to_state="rejected",
            triggered_by_user=fixture.cfo,
            trigger_reason="Catalogue reconciliation fixture.",
        )
        self.sanction_entry = CreditSanctionRegisterEntry.objects.create(
            approval_case=fixture.case,
            loan_application=fixture.application,
            member=fixture.member,
            sanction_decision=None,
            workflow_event=workflow,
            application_number=fixture.application.application_reference_number,
            borrower_name=fixture.member.display_name,
            borrower_type=fixture.member.member_type,
            requested_amount="500000.00",
            eligible_amount="400000.00",
            recommended_amount="400000.00",
            source_review_facts_json={},
            terminal_facts_json={},
            sanctioned_amount=None,
            authority_applied_summary="CFO and Director",
            approver_names_json=[],
            approver_decisions_json=[],
            approval_date=date(2026, 7, 1),
            decision="rejected",
            reasons="Rejected by governed approval.",
            recorded_by_user=fixture.cfo,
        )
        self.exception_entry = ExceptionRegisterEntry.objects.create(
            loan_application=fixture.application,
            exception_type="exceeds_loan_limit",
            description="Frozen permissible limit exceeded.",
            business_reason="Joint authority is required.",
            risk_assessment="Seasonal monitoring.",
            approval_case=fixture.case,
        )

    def test_credit_and_exception_reports_reuse_owner_registers_and_filters(self):
        auth = self.fixture._auth(self.fixture.cfo)

        sanction = get_with_query_bound(
            self,
            self.client,
            (
                "/api/v1/reports/credit-sanction/"
                "?financial_year=FY2026-27&decision=rejected"
            ),
            auth,
        )
        exception = get_with_query_bound(
            self,
            self.client,
            (
                "/api/v1/reports/exception/"
                "?status=pending&exception_type=exceeds_loan_limit"
            ),
            auth,
        )

        self.assertEqual(sanction.status_code, 200, sanction.content)
        self.assertEqual(exception.status_code, 200, exception.content)
        self.assertEqual(sanction.json()["pagination"]["total_count"], 1)
        self.assertEqual(
            sanction.json()["pagination"]["totals"],
            {"sanctioned_amount": "0.00"},
        )
        self.assertEqual(
            sanction.json()["data"][0]["credit_sanction_register_entry_id"],
            str(self.sanction_entry.pk),
        )
        self.assertEqual(exception.json()["pagination"]["total_count"], 1)
        self.assertEqual(
            exception.json()["data"][0]["exception_register_entry_id"],
            str(self.exception_entry.pk),
        )
        assert_validation_error(
            self,
            self.client.get(
                "/api/v1/reports/credit-sanction/?decision=unknown",
                **auth,
            ),
            "decision",
        )
        assert_validation_error(
            self,
            self.client.get(
                "/api/v1/reports/exception/?exception_type=unknown",
                **auth,
            ),
            "exception_type",
        )
