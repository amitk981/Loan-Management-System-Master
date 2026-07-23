from datetime import date

from django.test import Client, TestCase
from django.utils import timezone

from sfpcl_credit.applications.models import (
    LoanApplication,
    LoanRequestRegisterEntry,
)
from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant
from sfpcl_credit.identity.models import Permission, Role, RolePermission, User
from sfpcl_credit.legal_documents.models import ChecklistItem, DocumentChecklist
from sfpcl_credit.members.models import Member
from sfpcl_credit.tests.api_contracts import assert_pagination_shape


class ReportApiTests(TestCase):
    password = "ReportApiPass123!"

    def setUp(self):
        self.client = Client()
        self.auditor_role = Role.objects.create(
            role_code="internal_auditor",
            role_name="Internal Auditor",
        )
        self.auditor = self._user(
            self.auditor_role,
            "report.auditor@sfpcl.example",
        )
        self._grant(self.auditor_role, "reports.application_pipeline.read")
        ApprovalCaseReadScopeGrant.objects.create(
            role=self.auditor_role,
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
        )
        self.member = Member.objects.create(
            member_number="MEM-REPORT-001",
            member_type="individual_farmer",
            legal_name="Report Member",
            display_name="Report Member",
            folio_number="FOL-REPORT-001",
            membership_status="active",
            pan_encrypted="encrypted-report-pan",
            pan_hash="report-pan-hash",
            kyc_status="verified",
            default_status="no_default",
            created_by_user=self.auditor,
        )
        self.application = LoanApplication.objects.create(
            application_reference_number="LR-REPORT-001",
            member=self.member,
            borrower_type=self.member.member_type,
            application_date=date(2026, 4, 1),
            received_by_user=self.auditor,
            created_by_user=self.auditor,
            required_loan_amount="250000.00",
            declared_purpose="Crop finance",
            purpose_category="crop_production",
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            application_status=LoanApplication.STATUS_REFERENCE_GENERATED,
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
        )
        self.register_entry = LoanRequestRegisterEntry.objects.create(
            loan_application=self.application,
            application_reference_number="LR-REPORT-001",
            member=self.member,
            date_received=date(2026, 4, 1),
            reference_generated_date=date(2026, 4, 2),
            received_channel="assisted_digital",
            received_by_user=self.auditor,
            register_status="reference_generated",
            requested_amount="250000.00",
            declared_purpose="Crop finance",
            purpose_category="crop_production",
            borrower_name="Report Member",
            folio_number="FOL-REPORT-001",
            member_type="individual_farmer",
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            current_owner_role="credit_manager",
        )

    def test_application_pipeline_reconciles_to_the_loan_request_register(self):
        response = self.client.get(
            "/api/v1/reports/application-pipeline/",
            **self._auth(self.auditor),
        )

        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        assert_pagination_shape(self, body)
        self.assertEqual(body["pagination"]["total_count"], 1)
        self.assertEqual(
            body["data"],
            [
                {
                    "loan_request_register_entry_id": str(self.register_entry.pk),
                    "loan_application_id": str(self.application.pk),
                    "application_reference_number": "LR-REPORT-001",
                    "member_id": str(self.member.pk),
                    "borrower_name": "Report Member",
                    "date_received": "2026-04-01",
                    "reference_generated_date": "2026-04-02",
                    "received_channel": "assisted_digital",
                    "register_status": "reference_generated",
                    "requested_amount": "250000.00",
                    "declared_purpose": "Crop finance",
                    "purpose_category": "crop_production",
                    "member_type": "individual_farmer",
                    "current_stage": "credit_assessment",
                    "current_owner_role": "credit_manager",
                    "eligibility_status": "pending",
                    "sanction_status": "pending",
                    "documentation_status": "pending",
                    "disbursement_status": "pending",
                }
            ],
        )

    def test_documentation_readiness_reconciles_checklist_status_and_blockers(self):
        self._grant(self.auditor_role, "documents.checklist.read")
        application = LoanApplication.objects.create(
            application_reference_number="LR-DOC-REPORT-001",
            member=self.member,
            borrower_type=self.member.member_type,
            application_date=date(2026, 4, 3),
            received_by_user=self.auditor,
            created_by_user=self.auditor,
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            application_status=LoanApplication.STATUS_APPROVED_BY_SANCTION,
        )
        checklist = DocumentChecklist.objects.create(loan_application=application)
        ChecklistItem.objects.create(
            document_checklist=checklist,
            item_code="term_sheet",
            item_label="Term sheet",
            display_order=1,
            required_flag=True,
            applicable_flag=True,
            completion_status=ChecklistItem.STATUS_COMPLETE,
            applicability_source="approved_terms",
        )
        ChecklistItem.objects.create(
            document_checklist=checklist,
            item_code="loan_agreement",
            item_label="Loan agreement",
            display_order=2,
            required_flag=True,
            applicable_flag=True,
            completion_status=ChecklistItem.STATUS_PENDING,
            applicability_source="approved_terms",
        )

        response = self.client.get(
            "/api/v1/reports/documentation-readiness/?status=pending",
            **self._auth(self.auditor),
        )

        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        assert_pagination_shape(self, body)
        self.assertEqual(body["pagination"]["total_count"], 1)
        self.assertEqual(
            body["data"][0],
            {
                "document_checklist_id": str(checklist.pk),
                "loan_application_id": str(application.pk),
                "application_reference_number": "LR-DOC-REPORT-001",
                "member_id": str(self.member.pk),
                "borrower_name": "Report Member",
                "checklist_status": "in_progress",
                "required_item_count": 2,
                "completed_item_count": 1,
                "pending_item_count": 1,
                "blocker_codes": ["loan_agreement"],
                "created_at": checklist.created_at.isoformat().replace(
                    "+00:00",
                    "Z",
                ),
                "updated_at": checklist.updated_at.isoformat().replace(
                    "+00:00",
                    "Z",
                ),
            },
        )

    def test_application_pipeline_applies_inclusive_combined_filters_and_validation(self):
        matched = self.client.get(
            (
                "/api/v1/reports/application-pipeline/"
                "?from_date=2026-04-01&to_date=2026-04-01"
                "&status=reference_generated&stage=credit_assessment"
            ),
            **self._auth(self.auditor),
        )
        reversed_range = self.client.get(
            (
                "/api/v1/reports/application-pipeline/"
                "?from_date=2026-04-02&to_date=2026-04-01"
            ),
            **self._auth(self.auditor),
        )
        invalid_status = self.client.get(
            "/api/v1/reports/application-pipeline/?status=not-a-status",
            **self._auth(self.auditor),
        )
        invalid_stage = self.client.get(
            "/api/v1/reports/application-pipeline/?stage=not-a-stage",
            **self._auth(self.auditor),
        )
        malformed_date = self.client.get(
            "/api/v1/reports/application-pipeline/?from_date=01-04-2026",
            **self._auth(self.auditor),
        )

        self.assertEqual(matched.status_code, 200, matched.content)
        self.assertEqual(matched.json()["pagination"]["total_count"], 1)
        for response, field in (
            (reversed_range, "to_date"),
            (invalid_status, "status"),
            (invalid_stage, "stage"),
            (malformed_date, "from_date"),
        ):
            self.assertEqual(response.status_code, 400, response.content)
            self.assertEqual(
                response.json()["error"]["code"],
                "VALIDATION_ERROR",
            )
            self.assertIn(field, response.json()["error"]["field_errors"])

    def test_report_auth_and_object_scope_never_disclose_forbidden_totals(self):
        unauthenticated = self.client.get(
            "/api/v1/reports/application-pipeline/"
        )
        reader_role = Role.objects.create(
            role_code="report_scope_reader",
            role_name="Report Scope Reader",
        )
        reader = self._user(
            reader_role,
            "report.scope.reader@sfpcl.example",
        )
        self._grant(reader_role, "reports.application_pipeline.read")
        authorised_empty = self.client.get(
            "/api/v1/reports/application-pipeline/",
            **self._auth(reader),
        )
        RolePermission.objects.filter(
            role=reader_role,
            permission__permission_code="reports.application_pipeline.read",
        ).delete()
        forbidden = self.client.get(
            "/api/v1/reports/application-pipeline/",
            **self._auth(reader),
        )

        self.assertEqual(unauthenticated.status_code, 401)
        self.assertEqual(authorised_empty.status_code, 200)
        self.assertEqual(authorised_empty.json()["data"], [])
        self.assertEqual(
            authorised_empty.json()["pagination"]["total_count"],
            0,
        )
        self.assertEqual(forbidden.status_code, 403)
        self.assertNotIn("pagination", forbidden.json())
        self.assertNotIn("data", forbidden.json())

    def test_credit_manager_global_scope_is_limited_to_credit_assessment(self):
        credit_manager_role = Role.objects.create(
            role_code="credit_manager",
            role_name="Credit Manager",
        )
        credit_manager = self._user(
            credit_manager_role,
            "report.credit.manager@sfpcl.example",
        )
        self._grant(
            credit_manager_role,
            "reports.application_pipeline.read",
        )
        initial_application = LoanApplication.objects.create(
            application_reference_number="LR-REPORT-INITIAL",
            member=self.member,
            borrower_type=self.member.member_type,
            application_date=date(2026, 4, 2),
            received_by_user=self.auditor,
            created_by_user=self.auditor,
            current_stage=LoanApplication.STAGE_INITIAL,
            application_status=LoanApplication.STATUS_DRAFT,
        )
        LoanRequestRegisterEntry.objects.create(
            loan_application=initial_application,
            application_reference_number="LR-REPORT-INITIAL",
            member=self.member,
            date_received=date(2026, 4, 2),
            reference_generated_date=date(2026, 4, 2),
            received_channel="assisted_digital",
            received_by_user=self.auditor,
            borrower_name=self.member.display_name,
            current_stage=LoanApplication.STAGE_INITIAL,
        )

        response = self.client.get(
            "/api/v1/reports/application-pipeline/",
            **self._auth(credit_manager),
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 1)
        self.assertEqual(
            response.json()["data"][0]["loan_application_id"],
            str(self.application.pk),
        )

    def test_application_pipeline_pagination_is_stable_bounded_and_read_only(self):
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        application = LoanApplication.objects.create(
            application_reference_number="LR-REPORT-000",
            member=self.member,
            borrower_type=self.member.member_type,
            application_date=date(2026, 3, 31),
            received_by_user=self.auditor,
            created_by_user=self.auditor,
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
            application_status=LoanApplication.STATUS_REFERENCE_GENERATED,
            completeness_status=LoanApplication.COMPLETENESS_COMPLETE,
        )
        older = LoanRequestRegisterEntry.objects.create(
            loan_application=application,
            application_reference_number="LR-REPORT-000",
            member=self.member,
            date_received=date(2026, 3, 31),
            reference_generated_date=date(2026, 4, 1),
            received_channel="assisted_digital",
            received_by_user=self.auditor,
            borrower_name="Report Member",
            current_stage=LoanApplication.STAGE_CREDIT_ASSESSMENT,
        )
        from sfpcl_credit.identity.models import AuditLog

        auth = self._auth(self.auditor)
        audit_count = AuditLog.objects.count()
        with CaptureQueriesContext(connection) as queries:
            first = self.client.get(
                "/api/v1/reports/application-pipeline/?page=1&page_size=1",
                **auth,
            )
        second = self.client.get(
            "/api/v1/reports/application-pipeline/?page=2&page_size=1",
            **auth,
        )
        invalid_page = self.client.get(
            "/api/v1/reports/application-pipeline/?page=0",
            **auth,
        )
        invalid_page_size = self.client.get(
            "/api/v1/reports/application-pipeline/?page_size=not-a-number",
            **auth,
        )
        oversized_page = self.client.get(
            "/api/v1/reports/application-pipeline/?page_size=101",
            **auth,
        )

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(second.status_code, 200, second.content)
        self.assertEqual(first.json()["pagination"]["total_count"], 2)
        self.assertEqual(
            first.json()["data"][0]["loan_request_register_entry_id"],
            str(self.register_entry.pk),
        )
        self.assertEqual(
            second.json()["data"][0]["loan_request_register_entry_id"],
            str(older.pk),
        )
        self.assertLessEqual(len(queries), 10)
        self.assertEqual(AuditLog.objects.count(), audit_count)
        self.assertEqual(LoanRequestRegisterEntry.objects.count(), 2)
        for response, field in (
            (invalid_page, "page"),
            (invalid_page_size, "page_size"),
            (oversized_page, "page_size"),
        ):
            self.assertEqual(response.status_code, 400, response.content)
            self.assertIn(field, response.json()["error"]["field_errors"])

    def test_documentation_readiness_rejects_unknown_status_and_parameters(self):
        self._grant(self.auditor_role, "documents.checklist.read")
        invalid_status = self.client.get(
            "/api/v1/reports/documentation-readiness/?status=unknown",
            **self._auth(self.auditor),
        )
        unknown_filter = self.client.get(
            "/api/v1/reports/documentation-readiness/?stage=credit_assessment",
            **self._auth(self.auditor),
        )

        self.assertEqual(invalid_status.status_code, 400)
        self.assertIn(
            "status",
            invalid_status.json()["error"]["field_errors"],
        )
        self.assertEqual(unknown_filter.status_code, 400)
        self.assertIn(
            "stage",
            unknown_filter.json()["error"]["field_errors"],
        )

    def _user(self, role, email):
        user = User.objects.create(
            full_name=role.role_name,
            email=email,
            primary_role=role,
            password_hash="",
        )
        user.set_password(self.password)
        user.save(update_fields=["password_hash"])
        return user

    @staticmethod
    def _grant(role, *permission_codes):
        for code in permission_codes:
            permission, _created = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "reports",
                    "risk_level": "high",
                },
            )
            RolePermission.objects.get_or_create(role=role, permission=permission)

    def _auth(self, user):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        return {
            "HTTP_AUTHORIZATION": (
                f"Bearer {response.json()['data']['access_token']}"
            )
        }


class PortfolioReportApiTests(TestCase):
    password = "PortfolioReportPass123!"

    def setUp(self):
        from sfpcl_credit.identity.epic009_e2e_fixture import (
            build_ready_epic009_fixture,
        )

        self.client = Client()
        self.facts = build_ready_epic009_fixture(
            password=self.password,
            finance_email="portfolio.finance@sfpcl.example",
            credit_email="portfolio.credit@sfpcl.example",
            cfc_email="portfolio.cfc@sfpcl.example",
            borrower_email="portfolio.borrower@sfpcl.example",
        )
        self.actor = self.facts["finance"]
        self.account = self.facts["ready"]["account"]
        self._grant("reports.portfolio.read")

    def test_loan_portfolio_reconciles_to_scoped_loan_accounts(self):
        response = self.client.get(
            (
                "/api/v1/reports/loan-portfolio/"
                f"?as_of_date={timezone.localdate().isoformat()}"
                f"&status={self.account.loan_account_status}"
            ),
            **self._auth(),
        )

        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        assert_pagination_shape(self, body)
        self.assertEqual(body["pagination"]["total_count"], 1)
        self.assertEqual(
            body["data"][0],
            {
                "loan_account_id": str(self.account.pk),
                "loan_account_number": self.account.loan_account_number,
                "loan_application_id": str(self.account.loan_application_id),
                "member_id": str(self.account.member_id),
                "borrower_name": self.account.member.display_name,
                "loan_account_status": self.account.loan_account_status,
                "sanctioned_amount": f"{self.account.sanctioned_amount:.2f}",
                "disbursed_amount": f"{self.account.disbursed_amount:.2f}",
                "principal_outstanding": (
                    f"{self.account.principal_outstanding:.2f}"
                ),
                "interest_outstanding": (
                    f"{self.account.interest_outstanding:.2f}"
                ),
                "charges_outstanding": (
                    f"{self.account.charges_outstanding:.2f}"
                ),
                "total_outstanding": f"{self.account.total_outstanding:.2f}",
                "loan_type": self.account.loan_type,
                "tenure_start_date": (
                    self.account.tenure_start_date.isoformat()
                    if self.account.tenure_start_date
                    else None
                ),
                "tenure_end_date": (
                    self.account.tenure_end_date.isoformat()
                    if self.account.tenure_end_date
                    else None
                ),
                "repayment_date": self.account.repayment_date.isoformat(),
                "current_interest_rate": (
                    f"{self.account.current_interest_rate:.4f}"
                ),
                "created_at": self.account.created_at.isoformat().replace(
                    "+00:00",
                    "Z",
                ),
            },
        )

    def test_dpd_report_reconciles_to_the_latest_scoped_snapshot(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.monitoring.models import DpdStatus

        self._grant("reports.dpd.read", "monitoring.dpd.read")
        audit = AuditLog.objects.create(
            actor_user=self.actor,
            action="monitoring.dpd.calculated",
            entity_type="dpd_status",
            new_value_json={
                "loan_account_id": str(self.account.pk),
                "as_of_date": "2026-06-30",
            },
        )
        dpd = DpdStatus.objects.create(
            loan_account=self.account,
            as_of_date=date(2026, 6, 30),
            days_past_due=367,
            sop_bucket="one_to_two_years",
            principal_overdue_amount="1000.00",
            interest_overdue_amount="100.00",
            total_overdue_amount="1100.00",
            earliest_unpaid_due_date=date(2025, 6, 29),
            calculation_inputs_json={
                "policy_decision": {
                    "sop_policy_version": "SFPCL-SOP-DPD-1",
                }
            },
            calculated_by_user=self.actor,
            calculation_audit=audit,
        )
        type(self.account).objects.filter(pk=self.account.pk).update(
            current_dpd_status=dpd
        )

        response = self.client.get(
            (
                "/api/v1/reports/dpd/?as_of_date=2026-06-30"
                "&sop_bucket=one_to_two_years"
            ),
            **self._auth(),
        )

        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        assert_pagination_shape(self, body)
        self.assertEqual(body["pagination"]["total_count"], 1)
        self.assertEqual(
            body["data"][0],
            {
                "dpd_status_id": str(dpd.pk),
                "loan_account_id": str(self.account.pk),
                "loan_account_number": self.account.loan_account_number,
                "member_id": str(self.account.member_id),
                "borrower_name": self.account.member.display_name,
                "as_of_date": "2026-06-30",
                "days_past_due": 367,
                "sop_bucket": "one_to_two_years",
                "standard_bucket": None,
                "principal_overdue_amount": "1000.00",
                "interest_overdue_amount": "100.00",
                "total_overdue_amount": "1100.00",
                "earliest_unpaid_due_date": "2025-06-29",
                "loan_account_status": self.account.loan_account_status,
                "principal_outstanding": (
                    f"{self.account.principal_outstanding:.2f}"
                ),
            },
        )

    def test_portfolio_and_dpd_reject_invalid_controlled_filters(self):
        self._grant("reports.dpd.read", "monitoring.dpd.read")
        invalid_portfolio_date = self.client.get(
            "/api/v1/reports/loan-portfolio/?as_of_date=2026-13-01",
            **self._auth(),
        )
        invalid_portfolio_status = self.client.get(
            "/api/v1/reports/loan-portfolio/?status=unknown",
            **self._auth(),
        )
        invalid_dpd_date = self.client.get(
            "/api/v1/reports/dpd/?as_of_date=not-a-date",
            **self._auth(),
        )
        invalid_dpd_bucket = self.client.get(
            "/api/v1/reports/dpd/?sop_bucket=unknown",
            **self._auth(),
        )

        for response, field in (
            (invalid_portfolio_date, "as_of_date"),
            (invalid_portfolio_status, "status"),
            (invalid_dpd_date, "as_of_date"),
            (invalid_dpd_bucket, "sop_bucket"),
        ):
            self.assertEqual(response.status_code, 400, response.content)
            self.assertIn(field, response.json()["error"]["field_errors"])

    def _grant(self, *permission_codes):
        ReportApiTests._grant(self.actor.primary_role, *permission_codes)

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


class DisbursementPendingReportApiTests(TestCase):
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
        self.actor = fixture.actor
        self.reader = fixture.cfc
        fixture.fixture._grant(
            self.reader,
            "finance.disbursement.readiness",
            "finance.loan_account.read",
        )

    def test_disbursement_pending_reconciles_to_current_initiations(self):
        initiated = self.fixture._post(key="report-disbursement-initiation")
        self.assertEqual(initiated.status_code, 200, initiated.content)

        response = self.client.get(
            "/api/v1/reports/disbursement-pending/",
            **self.fixture._auth(self.reader),
        )

        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        assert_pagination_shape(self, body)
        self.assertEqual(body["pagination"]["total_count"], 1)
        from sfpcl_credit.disbursements.models import Disbursement
        from sfpcl_credit.loans.models import LoanAccount

        row = Disbursement.objects.get()
        account = LoanAccount.objects.select_related("member").get(
            pk=self.fixture.account_id
        )
        self.assertEqual(
            body["data"][0],
            {
                "disbursement_id": str(row.pk),
                "loan_account_id": str(account.pk),
                "loan_account_number": account.loan_account_number,
                "loan_application_id": str(account.loan_application_id),
                "member_id": str(account.member_id),
                "borrower_name": account.member.display_name,
                "disbursement_amount": f"{row.disbursement_amount:.2f}",
                "initiation_status": "initiated",
                "authorisation_status": "pending",
                "bank_transfer_status": "pending",
                "initiated_by_user_id": str(self.actor.pk),
                "initiated_by_name": self.actor.full_name,
                "initiated_at": row.initiated_at.isoformat().replace(
                    "+00:00",
                    "Z",
                ),
                "authorised_by_user_id": None,
                "authorised_at": None,
            },
        )

    def test_disbursement_pending_rejects_uncontracted_filters(self):
        response = self.client.get(
            "/api/v1/reports/disbursement-pending/?status=pending",
            **self.fixture._auth(self.reader),
        )

        self.assertEqual(response.status_code, 400, response.content)
        self.assertIn("status", response.json()["error"]["field_errors"])


class ComplianceDashboardReportApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_statutory_trackers import (
            StatutoryTrackerModuleTests,
        )

        fixture = StatutoryTrackerModuleTests(
            "test_section_186_calculate_uses_higher_limit_and_flags_excess"
        )
        fixture.setUp()
        fixture.client = Client()
        self.fixture = fixture
        self.client = fixture.client
        self.actor = fixture.cfo
        for permission in (
            "reports.compliance.read",
            "compliance.section186.read",
            "compliance.nbfc_test.create",
            "compliance.nbfc_test.read",
        ):
            fixture._grant(fixture.cfo_role, permission)

    def test_compliance_dashboard_reconciles_statutory_tracker_rows(self):
        from sfpcl_credit.compliance.modules.nbfc_principal_business_test import (
            NbfcPrincipalBusinessTestModule,
        )
        from sfpcl_credit.compliance.modules.section186_tracker import (
            Section186TrackerModule,
        )

        section_task, section_evidence = self.fixture._accepted_evidence(
            "SECTION_186_LIMIT"
        )
        section = Section186TrackerModule.calculate(
            actor=self.actor,
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
            actor=self.actor,
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

        response = self.client.get(
            (
                "/api/v1/reports/compliance-dashboard/"
                "?financial_year=FY2026-27"
            ),
            **self.fixture._auth(self.actor),
        )

        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        assert_pagination_shape(self, body)
        self.assertEqual(body["pagination"]["total_count"], 2)
        self.assertEqual(
            [
                (
                    row["report_type"],
                    row["report_record_id"],
                    row["financial_year"],
                    row["quarter"],
                )
                for row in body["data"]
            ],
            [
                ("section_186", str(section.pk), "FY2026-27", "Q1"),
                ("nbfc_principal_business", str(nbfc.pk), "FY2026-27", "Q1"),
            ],
        )
        self.assertTrue(body["data"][0]["within_limit_flag"])
        self.assertTrue(body["data"][1]["registration_triggered_flag"])

    def test_compliance_dashboard_rejects_malformed_financial_year(self):
        response = self.client.get(
            (
                "/api/v1/reports/compliance-dashboard/"
                "?financial_year=2026-27"
            ),
            **self.fixture._auth(self.actor),
        )

        self.assertEqual(response.status_code, 400, response.content)
        self.assertIn(
            "financial_year",
            response.json()["error"]["field_errors"],
        )
