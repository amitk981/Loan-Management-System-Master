from copy import deepcopy
from datetime import timedelta
from uuid import uuid4

from django.db import connection
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from sfpcl_credit.identity.models import AuditLog
from sfpcl_credit.loans.models import LoanAccount, LoanStatusHistory
from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest
from sfpcl_credit.tests.api_contracts import (
    assert_pagination_shape,
    assert_success_envelope,
)
from sfpcl_credit.workflows.models import WorkflowEvent


def _copy_for_insert(instance):
    """Build a fresh model through Django's public model-constructor interface."""
    values = {
        field.attname: deepcopy(getattr(instance, field.attname))
        for field in instance._meta.concrete_fields
        if not field.primary_key
    }
    return type(instance)(**values)


class LoanAccountReadApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_loan_account_creation_api import (
            LoanAccountCreationApiTests,
        )

        fixture = LoanAccountCreationApiTests(
            "test_terminal_sanction_creates_unfunded_account_terms_and_evidence"
        )
        fixture.setUp()
        created = fixture._post(
            {
                "sanction_decision_id": str(fixture.sanction.pk),
                "loan_account_number": "LN-2026-00025",
            }
        )
        self.assertEqual(created.status_code, 200, created.content)
        self.fixture = fixture
        self.account = LoanAccount.objects.get()
        self.reader = fixture._user("accounts_head", "Accounts Head")
        fixture._grant(self.reader, "finance.loan_account.read")
        self.client = Client()
        self.auth = fixture._auth(self.reader)

    def test_sanctioned_list_and_detail_are_exact_paginated_zero_write_projections(self):
        counts_before = self._business_counts()

        listing = self.client.get(
            "/api/v1/loan-accounts/?page=1&page_size=20", **self.auth
        )

        self.assertEqual(listing.status_code, 200, listing.content)
        assert_pagination_shape(self, listing.json())
        self.assertEqual(listing.json()["pagination"]["total_count"], 1)
        expected = {
            "loan_account_id": str(self.account.pk),
            "loan_account_number": "LN-2026-00025",
            "loan_application_id": str(self.fixture.application.pk),
            "application_reference_number": self.fixture.application.application_reference_number,
            "member": {
                "member_id": str(self.fixture.application.member_id),
                "display_name": "Ramesh Patil",
            },
            "sap_customer_code": None,
            "loan_type": "short_term",
            "facility_type": "short_term",
            "interest_rate_type": "floating",
            "current_interest_rate": "9.2500",
            "sanctioned_amount": "400000.00",
            "disbursed_amount": "0.00",
            "principal_outstanding": "0.00",
            "interest_outstanding": "0.00",
            "charges_outstanding": "0.00",
            "total_outstanding": "0.00",
            "loan_account_status": "sanctioned",
            "tenure_start_date": None,
            "tenure_end_date": None,
            "repayment_date": "2027-06-22",
            "tenure_months": 12,
            "created_at": self._utc(self.account.created_at),
            "activated_at": None,
        }
        self.assertEqual(listing.json()["data"], [expected])

        detail = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/", **self.auth
        )
        self.assertEqual(detail.status_code, 200, detail.content)
        assert_success_envelope(self, detail.json())
        self.assertEqual(detail.json()["data"], expected)
        self.assertEqual(self._business_counts(), counts_before)

        serialized = str(detail.json()) + str(listing.json())
        for forbidden in (
            "protected-pan",
            "protected-aadhaar",
            "bank_reference",
            "evidence_document",
            "checksum",
            "idempotency",
            "request_id_digest",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_populated_loan_account_collection_has_a_query_ceiling(self):
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                "/api/v1/loan-accounts/?page=1&page_size=20", **self.auth
            )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 1)
        self.assertLessEqual(len(queries), 30)

    def test_mixed_second_page_is_truthful_and_query_bounded_at_twenty_one_rows(self):
        self._assert_mixed_page_is_bounded(eligible_count=21, page=2)

    def test_mixed_full_first_page_query_count_is_independent_of_page_rows(self):
        created_ids = [self._clone_created_account(index) for index in range(20)]
        LoanAccount.objects.filter(pk=created_ids[-1]).update(
            sanctioned_amount="399999.00"
        )

        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                "/api/v1/loan-accounts/?page=1&page_size=20", **self.auth
            )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 20)
        self.assertEqual(len(response.json()["data"]), 20)
        self.assertLessEqual(len(queries), 35)

    def test_six_consecutive_drifted_rows_do_not_shift_exact_pages(self):
        created_ids = [self._clone_created_account(index) for index in range(26)]
        for account_id in created_ids[-6:]:
            audit = AuditLog.objects.get(
                action="finance.loan_account.created", entity_id=account_id
            )
            audit.new_value_json = {
                **audit.new_value_json,
                "actor_role_codes": [],
            }
            audit.save(update_fields=["new_value_json"])

        first = self.client.get(
            "/api/v1/loan-accounts/?page=1&page_size=20", **self.auth
        )
        last = self.client.get(
            "/api/v1/loan-accounts/?page=2&page_size=20", **self.auth
        )

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(last.status_code, 200, last.content)
        self.assertEqual(first.json()["pagination"]["total_count"], 21)
        self.assertEqual(first.json()["pagination"]["total_pages"], 2)
        self.assertEqual(len(first.json()["data"]), 20)
        self.assertEqual(
            [row["loan_account_id"] for row in last.json()["data"]],
            [str(self.account.pk)],
        )

    def test_mixed_last_page_is_truthful_and_query_bounded_at_one_hundred_one_rows(self):
        self._assert_mixed_page_is_bounded(eligible_count=101, page=6)

    def _assert_mixed_page_is_bounded(self, *, eligible_count, page):
        created_ids = [self.account.pk]
        for index in range(eligible_count):
            created_ids.append(self._clone_created_account(index))
        denied_id = created_ids.pop()
        LoanAccount.objects.filter(pk=denied_id).update(sanctioned_amount="399999.00")

        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(
                f"/api/v1/loan-accounts/?page={page}&page_size=20", **self.auth
            )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], eligible_count)
        self.assertEqual(response.json()["pagination"]["total_pages"], page)
        self.assertEqual(len(response.json()["data"]), 1)
        self.assertEqual(
            response.json()["data"][0]["loan_account_id"], str(self.account.pk)
        )
        self.assertLessEqual(len(queries), 35)

    def test_portfolio_authority_requires_both_source_role_and_current_permission(self):
        cfo = self.fixture._user("cfo", "CFO Portfolio Reader")
        self.fixture._grant(cfo, "finance.loan_account.read")
        cfo_detail = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/",
            **self.fixture._auth(cfo),
        )

        permission_only = self.fixture._user(
            "field_officer", "Intake Assignment Is Not Account Scope"
        )
        self.fixture._grant(permission_only, "finance.loan_account.read")
        permission_only_detail = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/",
            **self.fixture._auth(permission_only),
        )

        from sfpcl_credit.identity.models import RolePermission
        RolePermission.objects.filter(role=self.reader.primary_role).delete()
        role_only_detail = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/",
            **self.fixture._auth(self.reader),
        )

        self.assertEqual(cfo_detail.status_code, 200, cfo_detail.content)
        self.assertEqual(permission_only_detail.status_code, 403)
        self.assertEqual(role_only_detail.status_code, 403)

    def test_query_validation_and_missing_detail_are_strict_and_nondisclosing(self):
        for query in ("page=0", "page=2", "page_size=101", "page_size=abc"):
            with self.subTest(query=query):
                response = self.client.get(
                    f"/api/v1/loan-accounts/?{query}", **self.auth
                )
                self.assertEqual(response.status_code, 400, response.content)
                self.assertEqual(response.json()["error"]["code"], "VALIDATION_ERROR")
        missing = self.client.get(
            f"/api/v1/loan-accounts/{uuid4()}/", **self.auth
        )
        self.assertEqual(missing.status_code, 404, missing.content)
        self.assertEqual(missing.json()["error"]["code"], "NOT_FOUND")

    def test_source_supported_filters_and_dpd_deferral_are_explicit(self):
        matches = (
            f"search=00025",
            "loan_account_status=sanctioned",
            f"member_id={self.account.member_id}",
        )
        for query in matches:
            with self.subTest(query=query):
                response = self.client.get(
                    f"/api/v1/loan-accounts/?{query}", **self.auth
                )
                self.assertEqual(response.status_code, 200, response.content)
                self.assertEqual(response.json()["pagination"]["total_count"], 1)

        for query in (
            "search=does-not-exist",
            "loan_account_status=active",
            f"member_id={uuid4()}",
        ):
            with self.subTest(query=query):
                response = self.client.get(
                    f"/api/v1/loan-accounts/?{query}", **self.auth
                )
                self.assertEqual(response.status_code, 200, response.content)
                self.assertEqual(response.json()["data"], [])

        deferred = self.client.get(
            "/api/v1/loan-accounts/?dpd_bucket=current", **self.auth
        )
        self.assertEqual(deferred.status_code, 400, deferred.content)
        self.assertEqual(
            deferred.json()["error"]["field_errors"],
            {"dpd_bucket": "DPD filtering is owned by Epic 010 and is not available yet."},
        )

    def test_changed_creation_amount_fails_closed_without_existence_disclosure(self):
        LoanAccount.objects.filter(pk=self.account.pk).update(
            sanctioned_amount="399999.00"
        )

        detail = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/", **self.auth
        )
        listing = self.client.get("/api/v1/loan-accounts/", **self.auth)

        self.assertEqual(detail.status_code, 404, detail.content)
        self.assertEqual(listing.status_code, 200, listing.content)
        self.assertEqual(listing.json()["data"], [])

    def test_changed_creation_audit_body_is_excluded_from_count_and_page(self):
        audit = AuditLog.objects.get(
            action="finance.loan_account.created",
            entity_id=self.account.pk,
        )
        audit.new_value_json = {**audit.new_value_json, "outcome": "tampered"}
        audit.save(update_fields=["new_value_json"])

        listing = self.client.get("/api/v1/loan-accounts/", **self.auth)

        self.assertEqual(listing.status_code, 200, listing.content)
        self.assertEqual(listing.json()["pagination"]["total_count"], 0)
        self.assertEqual(listing.json()["data"], [])

    def test_nonqueryable_creation_drift_affects_neither_total_nor_page(self):
        audit = AuditLog.objects.get(
            action="finance.loan_account.created",
            entity_id=self.account.pk,
        )
        audit.new_value_json = {
            **audit.new_value_json,
            "actor_role_codes": [],
        }
        audit.save(update_fields=["new_value_json"])

        response = self.client.get("/api/v1/loan-accounts/", **self.auth)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])

    def test_source_role_scope_matrix_is_identical_for_list_and_detail(self):
        from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant

        company_secretary = self.fixture._user(
            "company_secretary", "Company Secretary Reader"
        )
        auditor = self.fixture._user("internal_auditor", "Scoped Auditor")
        credit = self.fixture._user("credit_manager", "Pre-activation Credit Reader")
        finance = self.fixture._user(
            "senior_manager_finance", "Unassigned Finance Reader"
        )
        cfc = self.fixture._user(
            "chief_financial_controller", "Unassigned CFC Reader"
        )
        for actor in (company_secretary, auditor, credit, finance, cfc):
            self.fixture._grant(actor, "finance.loan_account.read")
        ApprovalCaseReadScopeGrant.objects.create(
            role=auditor.primary_role,
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
            status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
        )

        for actor, allowed in (
            (company_secretary, True),
            (auditor, True),
            (credit, False),
            (finance, False),
            (cfc, False),
        ):
            with self.subTest(role=actor.primary_role.role_code):
                auth = self.fixture._auth(actor)
                detail = self.client.get(
                    f"/api/v1/loan-accounts/{self.account.pk}/", **auth
                )
                listing = self.client.get("/api/v1/loan-accounts/", **auth)
                self.assertEqual(detail.status_code, 200 if allowed else 404)
                self.assertEqual(
                    listing.json()["pagination"]["total_count"], 1 if allowed else 0
                )

    @staticmethod
    def _utc(value):
        return value.isoformat().replace("+00:00", "Z")

    @staticmethod
    def _business_counts():
        return (
            LoanAccount.objects.count(),
            LoanStatusHistory.objects.count(),
            AuditLog.objects.count(),
            WorkflowEvent.objects.count(),
        )

    def _clone_created_account(self, index):
        application = _copy_for_insert(self.account.loan_application)
        application.pk = uuid4()
        application.application_reference_number = f"LO-PAGE-{index:03d}"
        application.created_at = self.account.loan_application.created_at + timedelta(
            seconds=index + 1
        )
        application.updated_at = application.created_at
        application.save(force_insert=True)

        original_case = self.account.sanction_decision.approval_case
        approval_case = _copy_for_insert(original_case)
        approval_case.pk = uuid4()
        approval_case.loan_application = application
        approval_case.workflow_event = None
        approval_case.save(force_insert=True)

        sanction = _copy_for_insert(self.account.sanction_decision)
        sanction.pk = uuid4()
        sanction.loan_application = application
        sanction.approval_case = approval_case
        sanction.save(force_insert=True)

        account = _copy_for_insert(self.account)
        account.pk = uuid4()
        account.loan_application = application
        account.sanction_decision = sanction
        account.loan_account_number = f"LN-PAGE-{index:03d}"
        account.loan_account_number_normalized = account.loan_account_number.lower()
        account.created_at = self.account.created_at + timedelta(seconds=index + 1)
        account.save(force_insert=True)

        terms = _copy_for_insert(self.account.terms)
        terms.pk = uuid4()
        terms.loan_account = account
        terms.created_at = account.created_at
        terms.save(force_insert=True)

        original_history = self.account.status_history.get(outcome="created")
        history = _copy_for_insert(original_history)
        history.pk = uuid4()
        history.loan_account = account
        history.loan_application_id_snapshot = application.pk
        history.sanction_decision_id_snapshot = sanction.pk
        history.loan_terms_id_snapshot = terms.pk
        history.changed_at = account.created_at
        history.save(force_insert=True)

        original_audit = AuditLog.objects.get(
            action="finance.loan_account.created", entity_id=self.account.pk
        )
        audit = _copy_for_insert(original_audit)
        audit.pk = uuid4()
        audit.entity_id = account.pk
        audit.created_at = account.created_at
        audit.new_value_json = {
            **original_audit.new_value_json,
            "loan_account_id": str(account.pk),
            "loan_application_id": str(application.pk),
            "sanction_decision_id": str(sanction.pk),
            "loan_terms_id": str(terms.pk),
        }
        from sfpcl_credit.loans.modules.loan_account_lifecycle import (
            _canonical_manifest_json,
            _selector_manifest,
        )

        audit.old_value_json = _selector_manifest(audit.new_value_json)
        audit.selector_manifest_json = _canonical_manifest_json(
            audit.new_value_json
        )
        audit.selector_manifest_sha256 = audit.old_value_json[
            "selector_manifest_sha256"
        ]
        audit.save(force_insert=True)

        original_workflow = WorkflowEvent.objects.get(
            workflow_name="LoanAccountCreated", entity_id=self.account.pk
        )
        workflow = _copy_for_insert(original_workflow)
        workflow.pk = uuid4()
        workflow.entity_id = account.pk
        workflow.created_at = account.created_at
        workflow.save(force_insert=True)
        return account.pk


class ActiveLoanAccountReadApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_disbursement_transfer_success_api import (
            DisbursementTransferSuccessApiTests,
        )

        fixture = DisbursementTransferSuccessApiTests(
            "test_public_success_records_transfer_and_activates_exact_loan_atomically"
        )
        fixture.setUp()
        self.disbursed_at = timezone.now()
        transferred = fixture._post(
            bank_reference_number="RBL-READ-UTR-001",
            disbursed_at=self.disbursed_at,
        )
        self.assertEqual(transferred.status_code, 200, transferred.content)
        self.fixture = fixture
        self.account = LoanAccount.objects.get(pk=fixture.owner.fixture.application.loan_account.pk)
        self.account.refresh_from_db()
        self.reader = fixture.owner.fixture.fixture._user(
            "accounts_head", "Account Read Portfolio Owner"
        )
        fixture.owner.fixture.fixture._grant(
            self.reader, "finance.loan_account.read"
        )
        self.client = Client()
        self.auth = fixture.owner.fixture._auth(self.reader)

    def test_exact_transfer_projects_active_funded_amounts_and_activation_time(self):
        from sfpcl_credit.disbursements.modules.post_transfer_evidence import (
            resolve_post_transfer_evidence,
        )
        from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
            get_account_customer_code,
            get_customer_code_for_member,
        )

        self.assertIsNotNone(get_customer_code_for_member(self.account.member_id))
        self.assertIsNotNone(
            get_account_customer_code(
                application_id=self.account.loan_application_id,
                member_id=self.account.member_id,
                customer_code_id=self.account.sap_customer_code_id,
            )
        )
        self.assertIsNotNone(
            resolve_post_transfer_evidence(
                application_id=self.account.loan_application_id
            )
        )
        response = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/", **self.auth
        )

        self.assertEqual(response.status_code, 200, response.content)
        assert_success_envelope(self, response.json())
        data = response.json()["data"]
        self.assertEqual(data["loan_account_status"], "active")
        self.assertEqual(data["sap_customer_code"], "******-001")
        self.assertNotIn("READY-REAL-OWNER-001", str(response.json()))
        self.assertEqual(data["sanctioned_amount"], "400000.00")
        self.assertEqual(data["disbursed_amount"], "400000.00")
        self.assertEqual(data["principal_outstanding"], "400000.00")
        self.assertEqual(data["interest_outstanding"], "0.00")
        self.assertEqual(data["charges_outstanding"], "0.00")
        self.assertEqual(data["total_outstanding"], "400000.00")
        self.assertEqual(data["tenure_start_date"], self.disbursed_at.date().isoformat())
        self.assertEqual(
            data["tenure_end_date"],
            self.account.tenure_end_date.isoformat()
            if self.account.tenure_end_date
            else None,
        )
        self.assertEqual(data["activated_at"], self._utc(self.disbursed_at))
        self.assertNotIn("bank_reference_number", str(response.json()))
        self.assertNotIn("disbursement_advice_communication_id", str(response.json()))
        from sfpcl_credit.sap_workflow.models import SapCustomerCode

        SapCustomerCode.objects.filter(pk=self.account.sap_customer_code_id).update(
            status=SapCustomerCode.STATUS_INACTIVE
        )

        detail = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/", **self.auth
        )
        listing = self.client.get("/api/v1/loan-accounts/", **self.auth)

        self.assertEqual(detail.status_code, 404, detail.content)
        self.assertEqual(detail.json()["error"]["code"], "NOT_FOUND")
        self.assertEqual(listing.status_code, 200, listing.content)
        self.assertEqual(listing.json()["data"], [])
        self.assertEqual(listing.json()["pagination"]["total_count"], 0)

    def test_member_and_account_sap_reads_reject_newer_cross_application_drift_identically(self):
        from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest
        from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
            get_account_customer_code,
            get_customer_code_for_member,
        )

        original = SapCustomerProfileRequest.objects.get(
            loan_application_id=self.account.loan_application_id,
            request_status=SapCustomerProfileRequest.STATUS_COMPLETED,
        )
        later_application = _copy_for_insert(original.loan_application)
        later_application.pk = uuid4()
        later_application.application_reference_number = "LO-READ-CROSS-APP"
        later_application.created_at = original.loan_application.created_at + timedelta(days=1)
        later_application.save(force_insert=True)
        stale_cross_application = _copy_for_insert(original)
        stale_cross_application.pk = uuid4()
        stale_cross_application.loan_application = later_application
        stale_cross_application.created_at = original.created_at + timedelta(days=1)
        stale_cross_application.save(force_insert=True)

        member_decision = get_customer_code_for_member(self.account.member_id)
        account_decision = get_account_customer_code(
            application_id=self.account.loan_application_id,
            member_id=self.account.member_id,
            customer_code_id=self.account.sap_customer_code_id,
        )

        self.assertIsNone(member_decision)
        self.assertIsNone(account_decision)

    def test_completion_digest_drift_affects_neither_total_nor_page(self):
        request = SapCustomerProfileRequest.objects.get(
            loan_application_id=self.account.loan_application_id,
            request_status=SapCustomerProfileRequest.STATUS_COMPLETED,
        )
        audit = AuditLog.objects.get(
            entity_type="sap_customer_profile_request",
            entity_id=request.pk,
            action__in=("sap.customer_code_created", "sap.customer_code_reused"),
        )
        audit.new_value_json = {
            **audit.new_value_json,
            "completion_input_digest": "0" * 64,
        }
        audit.save(update_fields=["new_value_json"])

        response = self.client.get("/api/v1/loan-accounts/", **self.auth)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["pagination"]["total_count"], 0)
        self.assertEqual(response.json()["data"], [])

    def test_exact_active_scope_allows_assigned_finance_cfc_and_credit(self):
        finance = self.fixture.owner.fixture.actor
        cfc = self.fixture.actor
        credit = self.fixture.owner.fixture.fixture._user(
            "credit_manager", "Active Monitoring Credit Reader"
        )
        for actor in (finance, cfc, credit):
            self.fixture.owner.fixture.fixture._grant(
                actor, "finance.loan_account.read"
            )

        for actor in (finance, cfc, credit):
            with self.subTest(role=actor.primary_role.role_code):
                auth = self.fixture.owner.fixture._auth(actor)
                detail = self.client.get(
                    f"/api/v1/loan-accounts/{self.account.pk}/", **auth
                )
                listing = self.client.get("/api/v1/loan-accounts/", **auth)
                self.assertEqual(detail.status_code, 200, detail.content)
                self.assertEqual(listing.status_code, 200, listing.content)
                self.assertEqual(listing.json()["pagination"]["total_count"], 1)

    @staticmethod
    def _utc(value):
        return value.isoformat().replace("+00:00", "Z")
