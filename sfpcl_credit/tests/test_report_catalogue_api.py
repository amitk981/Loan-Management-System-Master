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
