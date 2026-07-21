import json
import tempfile
from datetime import date, datetime, timezone

from django.db import connection
from django.test import Client, TestCase, override_settings
from django.test.utils import CaptureQueriesContext

@override_settings(DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-quarterly-mis-tests-"))
class QuarterlyMisApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.identity.models import Permission, RolePermission
        from sfpcl_credit.tests.test_loan_schedule_ledger_api import (
            LoanScheduleLedgerApiTests,
        )
        fixture = LoanScheduleLedgerApiTests(
            "test_authorised_reader_gets_ordered_decimal_schedule_truth"
        )
        fixture.setUp()
        self.account = fixture.account
        self.actor = fixture.fixture.reader
        self.identity_fixture = fixture.fixture.fixture.owner.fixture.fixture
        self.auth_fixture = fixture.fixture.fixture.owner.fixture
        self.auth = fixture.auth
        self.client = Client()
        from sfpcl_credit.loans.models import LoanStatusHistory
        LoanStatusHistory.objects.create(
            loan_account=self.account,
            from_status="sanctioned",
            to_status="active",
            reason="Synthetic quarter-cutoff activation truth.",
            changed_by_user=self.actor,
            changed_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
            loan_application_id_snapshot=self.account.loan_application_id,
            member_id_snapshot=self.account.member_id,
            sanction_decision_id_snapshot=self.account.sanction_decision_id,
            sap_customer_code_id_snapshot=self.account.sap_customer_code_id,
            loan_terms_id_snapshot=self.account.terms.pk,
            outcome="activated",
        )
        self.account.disbursements.update(
            disbursed_at=datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc)
        )
        for code in (
            "monitoring.dpd.read",
            "monitoring.dpd.calculate",
            "monitoring.mis.generate",
            "monitoring.mis.submit",
            "monitoring.mis.review",
            "reports.export",
        ):
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "monitoring",
                    "risk_level": "high",
                },
            )
            RolePermission.objects.get_or_create(
                role=self.actor.primary_role,
                permission=permission,
            )
    def test_generate_freezes_cutoff_totals_and_exact_replay(self):
        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.monitoring.models import PortfolioSnapshot, QuarterlyMisReport
        RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=date(2025, 6, 29),
            principal_due="1000.00",
            interest_due="100.00",
            charges_due="0.00",
            total_due="1100.00",
            schedule_status="pending",
        )
        dpd = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2026-06-30"}),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(dpd.status_code, 200, dpd.content)
        with CaptureQueriesContext(connection) as queries:
            first = self._generate()
        replay = self._generate()
        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        data = first.json()["data"]
        self.assertEqual(replay.json()["data"], data)
        self.assertEqual(data["financial_year"], "FY2026-27")
        self.assertEqual(data["quarter"], "Q1")
        self.assertEqual(data["as_of_date"], "2026-06-30")
        self.assertEqual(data["revision"], 1)
        self.assertEqual(data["status"], "draft")
        self.assertEqual(data["totals"]["active_loans_count"], 1)
        self.assertEqual(data["totals"]["sanctioned_amount"], "400000.00")
        self.assertEqual(data["totals"]["disbursed_amount"], "400000.00")
        self.assertEqual(data["totals"]["principal_outstanding_amount"], "400000.00")
        self.assertEqual(data["totals"]["interest_outstanding_amount"], "0.00")
        self.assertEqual(data["totals"]["repayments_received_in_quarter"], "0.00")
        self.assertEqual(data["totals"]["loans_overdue_beyond_one_year_count"], 1)
        self.assertEqual(data["totals"]["dpd_bucket_counts"]["one_to_two_years"], 1)
        self.assertEqual(data["availability"]["grace_period_count"], "unavailable")
        self.assertEqual(data["availability"]["grievances_open_count"], "unavailable")
        self.assertEqual(QuarterlyMisReport.objects.count(), 1)
        self.assertEqual(PortfolioSnapshot.objects.count(), 1)
        snapshot = PortfolioSnapshot.objects.get()
        self.assertEqual(snapshot.total_active_loans_count, 1)
        self.assertEqual(str(snapshot.total_sanctioned_amount), "400000.00")
        self.assertEqual(snapshot.dpd_bucket_summary_json["one_to_two_years"], 1)
        self.assertIsNone(snapshot.default_cases_count)
        self.assertIsNotNone(data["report_document_id"])
        self.assertIsNotNone(data["excel_document_id"])
        self.assertLessEqual(len(queries), 40)
    def test_detail_and_bounded_drilldown_read_only_frozen_snapshot(self):
        from sfpcl_credit.loans.models import RepaymentSchedule
        RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=date(2025, 6, 29),
            principal_due="1000.00",
            interest_due="100.00",
            charges_due="0.00",
            total_due="1100.00",
            schedule_status="pending",
        )
        self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2026-06-30"}),
            content_type="application/json",
            **self.auth,
        )
        generated = self._generate().json()["data"]
        type(self.account).objects.filter(pk=self.account.pk).update(
            principal_outstanding="1.00", interest_outstanding="2.00", total_outstanding="3.00"
        )
        detail = self.client.get(
            f"/api/v1/quarterly-mis-reports/{generated['quarterly_mis_report_id']}/",
            **self.auth,
        )
        rows = self.client.get(
            f"/api/v1/quarterly-mis-reports/{generated['quarterly_mis_report_id']}/drill-down/"
            "?page=1&page_size=20",
            **self.auth,
        )
        self.assertEqual(detail.status_code, 200, detail.content)
        self.assertEqual(detail.json()["data"], generated)
        self.assertEqual(rows.status_code, 200, rows.content)
        self.assertEqual(rows.json()["pagination"]["total_count"], 1)
        self.assertEqual(rows.json()["pagination"]["page"], 1)
        self.assertEqual(rows.json()["data"][0]["loan_account_id"], str(self.account.pk))
        self.assertEqual(rows.json()["data"][0]["principal_outstanding_amount"], "400000.00")
        self.assertEqual(rows.json()["data"][0]["interest_outstanding_amount"], "0.00")
        self.assertEqual(rows.json()["data"][0]["default_status"], "unavailable")
        self.assertEqual(rows.json()["data"][0]["disbursement_date"], "2026-06-01")
        self.assertIn("loan_status_history_id", rows.json()["data"][0]["source_ids"])
        self.assertIn("repayment_ledger_entry_ids", rows.json()["data"][0]["source_ids"])
    def test_submit_then_distinct_cfo_review_retains_audited_revision(self):
        from sfpcl_credit.identity.models import AuditLog
        self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2026-06-30"}),
            content_type="application/json",
            **self.auth,
        )
        report_id = self._generate().json()["data"]["quarterly_mis_report_id"]
        cfo = self.identity_fixture._user("cfo", "Quarterly MIS CFO")
        for code in ("finance.loan_account.read", "monitoring.mis.review"):
            self.identity_fixture._grant(cfo, code)
        cfo_auth = self.auth_fixture._auth(cfo)
        out_of_order = self.client.post(
            f"/api/v1/quarterly-mis-reports/{report_id}/mark-reviewed/",
            data="{}",
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="mis-review-before-submit",
            **cfo_auth,
        )
        submitted = self.client.post(
            f"/api/v1/quarterly-mis-reports/{report_id}/submit-to-cfo/",
            data=json.dumps({"submitted_to_user_id": str(cfo.pk)}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="mis-submit-q1-r1",
            **self.auth,
        )
        reviewed = self.client.post(
            f"/api/v1/quarterly-mis-reports/{report_id}/mark-reviewed/",
            data="{}",
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="mis-review-q1-r1",
            **cfo_auth,
        )
        submitted_replay = self.client.post(
            f"/api/v1/quarterly-mis-reports/{report_id}/submit-to-cfo/",
            data=json.dumps({"submitted_to_user_id": str(cfo.pk)}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="mis-submit-q1-r1",
            **self.auth,
        )
        reviewed_replay = self.client.post(
            f"/api/v1/quarterly-mis-reports/{report_id}/mark-reviewed/",
            data="{}",
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="mis-review-q1-r1",
            **cfo_auth,
        )
        revision = self._generate(key="quarterly-mis-generate-q1-r2")
        self.assertEqual(out_of_order.status_code, 409, out_of_order.content)
        self.assertEqual(submitted.status_code, 200, submitted.content)
        self.assertEqual(submitted.json()["data"]["status"], "submitted")
        self.assertIsNotNone(submitted.json()["data"]["submitted_at"])
        self.assertEqual(reviewed.status_code, 200, reviewed.content)
        self.assertEqual(reviewed.json()["data"]["status"], "reviewed")
        self.assertIsNotNone(reviewed.json()["data"]["reviewed_at"])
        self.assertEqual(submitted_replay.json()["data"], submitted.json()["data"])
        self.assertEqual(reviewed_replay.json()["data"], reviewed.json()["data"])
        self.assertEqual(revision.status_code, 200, revision.content)
        self.assertEqual(revision.json()["data"]["revision"], 2)
        self.assertEqual(revision.json()["data"]["status"], "draft")
        self.assertNotEqual(revision.json()["data"]["quarterly_mis_report_id"], report_id)
        self.assertEqual(AuditLog.objects.filter(action="monitoring.mis.submitted").count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="monitoring.mis.reviewed").count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="monitoring.mis.transition_rejected").count(), 1
        )
    def test_pdf_and_excel_exports_reconcile_to_frozen_report(self):
        import io
        import zipfile
        from pypdf import PdfReader
        from sfpcl_credit.documents.models import DocumentFile
        from sfpcl_credit.documents.storage import LocalDocumentStorage
        from sfpcl_credit.identity.models import AuditLog
        self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2026-06-30"}),
            content_type="application/json",
            **self.auth,
        )
        generated = self._generate().json()["data"]
        pdf = self.client.get(
            f"/api/v1/quarterly-mis-reports/{generated['quarterly_mis_report_id']}/export/"
            "?format=pdf",
            **self.auth,
        )
        excel = self.client.get(
            f"/api/v1/quarterly-mis-reports/{generated['quarterly_mis_report_id']}/export/"
            "?format=xlsx",
            **self.auth,
        )
        self.assertEqual(pdf.status_code, 200, pdf.content)
        self.assertEqual(excel.status_code, 200, excel.content)
        self.assertEqual(pdf.json()["data"]["totals"], generated["totals"])
        self.assertEqual(excel.json()["data"]["totals"], generated["totals"])
        storage = LocalDocumentStorage()
        pdf_bytes = storage.read_verified(
            DocumentFile.objects.get(pk=pdf.json()["data"]["document_id"])
        )
        xlsx_bytes = storage.read_verified(
            DocumentFile.objects.get(pk=excel.json()["data"]["document_id"])
        )
        pdf_text = " ".join(
            page.extract_text() or "" for page in PdfReader(io.BytesIO(pdf_bytes)).pages
        )
        self.assertIn("FY2026-27 Q1", pdf_text)
        for value in (
            "400000.00",
            "0.00",
            "one_to_two_years",
            "unavailable",
            self.account.loan_account_number,
        ):
            self.assertIn(value, pdf_text)
        with zipfile.ZipFile(io.BytesIO(xlsx_bytes)) as workbook:
            sheet = workbook.read("xl/worksheets/sheet1.xml").decode("utf-8")
        self.assertIn("FY2026-27", sheet)
        self.assertIn("400000.00", sheet)
        self.assertIn("one_to_two_years", sheet)
        self.assertIn("availability.grace_period_count", sheet)
        self.assertEqual(AuditLog.objects.filter(action="monitoring.mis.exported").count(), 2)
    def test_list_validation_permissions_and_missing_owner_truth_fail_closed(self):
        from sfpcl_credit.identity.models import Permission, RolePermission
        missing = self._generate()
        invalid = self.client.post(
            "/api/v1/quarterly-mis-reports/generate/",
            data=json.dumps(
                {
                    "financial_year": "FY2026-27",
                    "quarter": "Q1",
                    "as_of_date": "2026-06-29",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="mis-invalid-cutoff",
            **self.auth,
        )
        self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2026-06-30"}),
            content_type="application/json",
            **self.auth,
        )
        report = self._generate().json()["data"]
        unknown = self.client.post(
            "/api/v1/quarterly-mis-reports/generate/",
            data=json.dumps(
                {
                    "financial_year": "FY2026-27",
                    "quarter": "Q1",
                    "as_of_date": "2026-06-30",
                    "live_total": "1.00",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="mis-unknown-field",
            **self.auth,
        )
        missing_key = self.client.post(
            "/api/v1/quarterly-mis-reports/generate/",
            data=json.dumps(
                {
                    "financial_year": "FY2026-27",
                    "quarter": "Q1",
                    "as_of_date": "2026-06-30",
                }
            ),
            content_type="application/json",
            **self.auth,
        )
        listing = self.client.get(
            "/api/v1/quarterly-mis-reports/?financial_year=FY2026-27&quarter=Q1"
            "&page=1&page_size=20",
            **self.auth,
        )
        permission = Permission.objects.get(permission_code="monitoring.mis.generate")
        RolePermission.objects.filter(
            role=self.actor.primary_role, permission=permission
        ).delete()
        denied_generate = self._generate()
        read_permission = Permission.objects.get(permission_code="finance.loan_account.read")
        RolePermission.objects.filter(
            role=self.actor.primary_role, permission=read_permission
        ).delete()
        denied_read = self.client.get(
            f"/api/v1/quarterly-mis-reports/{report['quarterly_mis_report_id']}/",
            **self.auth,
        )
        self.assertEqual(missing.status_code, 409, missing.content)
        self.assertEqual(invalid.status_code, 400, invalid.content)
        self.assertEqual(unknown.status_code, 400, unknown.content)
        self.assertEqual(missing_key.status_code, 400, missing_key.content)
        self.assertEqual(listing.status_code, 200, listing.content)
        self.assertEqual(listing.json()["pagination"]["total_count"], 1)
        self.assertEqual(listing.json()["data"][0]["quarterly_mis_report_id"], report["quarterly_mis_report_id"])
        self.assertEqual(denied_generate.status_code, 403, denied_generate.content)
        self.assertEqual(denied_read.status_code, 403, denied_read.content)
    def _generate(self, *, key="quarterly-mis-generate-q1-r1"):
        return self.client.post(
            "/api/v1/quarterly-mis-reports/generate/",
            data=json.dumps(
                {
                    "financial_year": "FY2026-27",
                    "quarter": "Q1",
                    "as_of_date": "2026-06-30",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=key,
            **self.auth,
        )

@override_settings(DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-mis-reconcile-tests-"))
class QuarterlyMisReconciliationApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.identity.models import Permission, RolePermission
        from sfpcl_credit.tests.test_repayment_allocation_api import RepaymentAllocationApiTests
        fixture = RepaymentAllocationApiTests(
            "test_partial_receipt_reduces_principal_and_appends_immutable_evidence"
        )
        fixture.setUp()
        self.fixture = fixture
        self.account = fixture.account
        self.actor = fixture.actor
        self.auth = fixture.auth
        self.client = Client()
        for code in (
            "monitoring.dpd.read",
            "monitoring.dpd.calculate",
            "monitoring.mis.generate",
        ):
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "monitoring",
                    "risk_level": "high",
                },
            )
            RolePermission.objects.get_or_create(role=self.actor.primary_role, permission=permission)
    def test_report_reconciles_posted_allocation_without_mutating_owner_rows(self):
        from sfpcl_credit.loans.models import RepaymentAllocation, RepaymentLedgerEntry
        captured = self.fixture.fixture._capture(
            self.fixture.fixture._payload(), "mis-reconciliation-repayment"
        )
        repayment_id = captured.json()["data"]["repayment_id"]
        self.fixture._schedule("400000.00")
        allocated = self.fixture._allocate(repayment_id)
        self.assertEqual(allocated.status_code, 200, allocated.content)
        self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/dpd-status/calculate/",
            data=json.dumps({"as_of_date": "2026-12-31"}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="quarterly-mis-reconcile-q3",
            **self.auth,
        )
        allocation_before = RepaymentAllocation.objects.values().get(repayment_id=repayment_id)
        ledger_before = RepaymentLedgerEntry.objects.values().get(allocation__repayment_id=repayment_id)
        response = self.client.post(
            "/api/v1/quarterly-mis-reports/generate/",
            data=json.dumps(
                {
                    "financial_year": "FY2026-27",
                    "quarter": "Q3",
                    "as_of_date": "2026-12-31",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="quarterly-mis-reconcile-q3",
            **self.auth,
        )
        self.assertEqual(response.status_code, 200, response.content)
        totals = response.json()["data"]["totals"]
        self.assertEqual(totals["principal_outstanding_amount"], "300000.00")
        self.assertEqual(totals["repayments_received_in_quarter"], "100000.00")
        self.assertEqual(totals["dpd_bucket_counts"]["current"], 1)
        self.assertEqual(
            RepaymentAllocation.objects.values().get(repayment_id=repayment_id), allocation_before
        )
        self.assertEqual(
            RepaymentLedgerEntry.objects.values().get(allocation__repayment_id=repayment_id),
            ledger_before,
        )
