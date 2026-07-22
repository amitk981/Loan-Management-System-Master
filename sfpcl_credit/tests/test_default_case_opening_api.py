import json
from datetime import date
from uuid import uuid4

from django.test import Client, TestCase

from sfpcl_credit.tests.api_contracts import assert_pagination_shape


class DefaultCaseOpeningApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.identity.models import Permission, RolePermission
        from sfpcl_credit.tests.test_loan_schedule_ledger_api import (
            LoanScheduleLedgerApiTests,
        )

        fixture = LoanScheduleLedgerApiTests(
            "test_authorised_reader_gets_ordered_decimal_schedule_truth"
        )
        fixture.setUp()
        self.fixture = fixture
        self.account = fixture.account
        self.client = Client()
        user_fixture = fixture.fixture.fixture.owner.fixture.fixture
        auth_fixture = fixture.fixture.fixture.owner.fixture
        self.actor = user_fixture._user("credit_manager", "Default Credit Manager")
        user_fixture._grant(self.actor, "finance.loan_account.read")
        self.auth = auth_fixture._auth(self.actor)
        for code, risk in (
            ("defaults.case.read", "medium"),
            ("defaults.case.open", "high"),
        ):
            permission, _ = Permission.objects.get_or_create(
                permission_code=code,
                defaults={
                    "permission_name": code,
                    "module_name": "defaults",
                    "risk_level": risk,
                },
            )
            RolePermission.objects.get_or_create(
                role=self.actor.primary_role,
                permission=permission,
            )

    def test_missed_scheduled_principal_opens_one_audited_case(self):
        from sfpcl_credit.defaults.models import DefaultCase
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.workflows.models import WorkflowEvent

        due_date = date(2026, 6, 22)
        RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=due_date,
            principal_due="1000.00",
            interest_due="100.00",
            charges_due="0.00",
            total_due="1100.00",
            schedule_status="pending",
        )
        servicing_before = type(self.account).objects.values(
            "principal_outstanding",
            "interest_outstanding",
            "charges_outstanding",
            "total_outstanding",
            "current_dpd_status_id",
        ).get(pk=self.account.pk)

        response = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/default-cases/open/",
            data=json.dumps(
                {
                    "trigger_event": "missed_principal_repayment",
                    "scheduled_due_date": due_date.isoformat(),
                    "reason": "Scheduled principal repayment missed.",
                }
            ),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200, response.content)
        row = DefaultCase.objects.get()
        self.assertEqual(
            response.json()["data"],
            {
                "default_case_id": str(row.pk),
                "default_case_status": "grace_period_active",
                "grace_period_start_date": "2026-06-22",
                "grace_period_end_date": "2026-09-22",
                "available_actions": [],
            },
        )
        self.assertEqual(row.opened_by_user_id, self.actor.pk)
        self.assertEqual(row.opening_audit.action, "default.case_opened")
        self.assertEqual(
            row.opening_audit.new_value_json,
            {
                "loan_account_id": str(self.account.pk),
                "member_id": str(self.account.member_id),
                "default_case_id": str(row.pk),
                "trigger_event": "missed_principal_repayment",
                "scheduled_due_date": "2026-06-22",
                "default_case_status": "grace_period_active",
            },
        )
        event = WorkflowEvent.objects.get(
            workflow_name="default_case",
            entity_type="default_case",
            entity_id=row.pk,
        )
        self.assertIsNone(event.from_state)
        self.assertEqual(event.to_state, "grace_period_active")
        self.assertEqual(event.triggered_by_user_id, self.actor.pk)
        self.assertEqual(
            AuditLog.objects.filter(action="default.case_opened").count(), 1
        )
        self.assertEqual(
            type(self.account).objects.values(*servicing_before.keys()).get(
                pk=self.account.pk
            ),
            servicing_before,
        )

    def test_exact_replay_converges_on_original_case_and_transition(self):
        from sfpcl_credit.defaults.models import DefaultCase
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.workflows.models import WorkflowEvent

        due_date = date(2026, 6, 22)
        RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=due_date,
            principal_due="1000.00",
            interest_due="0.00",
            charges_due="0.00",
            total_due="1000.00",
            schedule_status="pending",
        )
        payload = {
            "trigger_event": "missed_principal_repayment",
            "scheduled_due_date": due_date.isoformat(),
            "reason": "Scheduled principal repayment missed.",
        }
        first = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/default-cases/open/",
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth,
        )
        replay = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/default-cases/open/",
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], first.json()["data"])
        self.assertEqual(DefaultCase.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="default.case_opened").count(), 1
        )
        self.assertEqual(
            WorkflowEvent.objects.filter(
                workflow_name="default_case", to_state="grace_period_active"
            ).count(),
            1,
        )

    def test_scoped_detail_and_filtered_list_return_the_same_case_contract(self):
        from sfpcl_credit.loans.models import RepaymentSchedule

        due_date = date(2026, 6, 22)
        RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=due_date,
            principal_due="1000.00",
            interest_due="0.00",
            charges_due="0.00",
            total_due="1000.00",
            schedule_status="pending",
        )
        opened = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/default-cases/open/",
            data=json.dumps(
                {
                    "trigger_event": "missed_principal_repayment",
                    "scheduled_due_date": due_date.isoformat(),
                    "reason": "Missed principal.",
                }
            ),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(opened.status_code, 200, opened.content)
        expected = opened.json()["data"]

        detail = self.client.get(
            f"/api/v1/default-cases/{expected['default_case_id']}/", **self.auth
        )
        listing = self.client.get(
            "/api/v1/default-cases/"
            f"?default_case_status=grace_period_active"
            f"&member_id={self.account.member_id}"
            f"&loan_account_id={self.account.pk}&page=1&page_size=20",
            **self.auth,
        )

        self.assertEqual(detail.status_code, 200, detail.content)
        detail_data = detail.json()["data"]
        for field, value in expected.items():
            self.assertEqual(detail_data[field], value)
        self.assertEqual(detail_data["loan_account_id"], str(self.account.pk))
        self.assertEqual(detail_data["member_id"], str(self.account.member_id))
        self.assertEqual(detail_data["trigger_event"], "missed_principal_repayment")
        self.assertEqual(detail_data["scheduled_due_date"], "2026-06-22")
        self.assertEqual(listing.status_code, 200, listing.content)
        assert_pagination_shape(self, listing.json())
        self.assertEqual(listing.json()["pagination"]["total_count"], 1)
        self.assertEqual(listing.json()["data"], [detail_data])

    def test_invalid_unpaid_claims_and_denied_or_foreign_opens_are_zero_write(self):
        from sfpcl_credit.defaults.models import DefaultCase
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import RepaymentSchedule
        from sfpcl_credit.workflows.models import WorkflowEvent

        due_date = date(2026, 6, 22)
        RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=due_date,
            principal_due="0.00",
            interest_due="100.00",
            charges_due="0.00",
            total_due="100.00",
            schedule_status="pending",
        )
        valid = {
            "trigger_event": "missed_principal_repayment",
            "scheduled_due_date": due_date.isoformat(),
            "reason": "Caller-provided explanation only.",
        }
        user_fixture = self.fixture.fixture.fixture.owner.fixture.fixture
        auth_fixture = self.fixture.fixture.fixture.owner.fixture
        denied_actor = user_fixture._user("field_officer", "Denied Default Opener")
        user_fixture._grant(
            denied_actor, "finance.loan_account.read", "defaults.case.open"
        )
        denied_auth = auth_fixture._auth(denied_actor)
        cases = (
            (self.account.pk, valid, self.auth, 409),
            (
                self.account.pk,
                {**valid, "scheduled_due_date": "2099-01-01"},
                self.auth,
                400,
            ),
            (self.account.pk, {**valid, "missed": True}, self.auth, 400),
            (uuid4(), valid, self.auth, 404),
            (self.account.pk, valid, denied_auth, 403),
        )
        for loan_id, payload, auth, expected_status in cases:
            with self.subTest(expected_status=expected_status, payload=payload):
                response = self.client.post(
                    f"/api/v1/loan-accounts/{loan_id}/default-cases/open/",
                    data=json.dumps(payload),
                    content_type="application/json",
                    **auth,
                )
                self.assertEqual(expected_status, response.status_code, response.content)
                self.assertEqual(DefaultCase.objects.count(), 0)
                self.assertEqual(
                    AuditLog.objects.filter(action="default.case_opened").count(), 0
                )
                self.assertEqual(
                    WorkflowEvent.objects.filter(workflow_name="default_case").count(), 0
                )

    def test_auditor_with_active_scope_can_read_but_cannot_open(self):
        from sfpcl_credit.approvals.models import ApprovalCaseReadScopeGrant
        from sfpcl_credit.loans.models import RepaymentSchedule

        due_date = date(2026, 6, 22)
        RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=due_date,
            principal_due="1000.00",
            interest_due="0.00",
            charges_due="0.00",
            total_due="1000.00",
            schedule_status="pending",
        )
        payload = {
            "trigger_event": "missed_principal_repayment",
            "scheduled_due_date": due_date.isoformat(),
            "reason": "Missed principal.",
        }
        opened = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/default-cases/open/",
            data=json.dumps(payload),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(opened.status_code, 200, opened.content)

        user_fixture = self.fixture.fixture.fixture.owner.fixture.fixture
        auth_fixture = self.fixture.fixture.fixture.owner.fixture
        auditor = user_fixture._user("internal_auditor", "Default Case Auditor")
        user_fixture._grant(auditor, "defaults.case.read")
        ApprovalCaseReadScopeGrant.objects.create(
            role=auditor.primary_role,
            scope_type=ApprovalCaseReadScopeGrant.SCOPE_AUDIT_READONLY,
            status=ApprovalCaseReadScopeGrant.STATUS_ACTIVE,
        )
        auditor_auth = auth_fixture._auth(auditor)

        detail = self.client.get(
            f"/api/v1/default-cases/{opened.json()['data']['default_case_id']}/",
            **auditor_auth,
        )
        denied_open = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/default-cases/open/",
            data=json.dumps(payload),
            content_type="application/json",
            **auditor_auth,
        )

        self.assertEqual(detail.status_code, 200, detail.content)
        self.assertEqual(detail.json()["data"]["available_actions"], [])
        self.assertEqual(denied_open.status_code, 403, denied_open.content)

    def test_allocated_principal_obligation_does_not_open_a_case(self):
        from sfpcl_credit.defaults.models import DefaultCase
        from sfpcl_credit.loans.models import RepaymentSchedule

        user_fixture = self.fixture.fixture.fixture.owner.fixture.fixture
        user_fixture._grant(
            self.actor,
            "finance.repayment.create",
            "finance.repayment.mark_sap_posted",
            "finance.repayment.allocate",
        )
        due_date = date(2026, 6, 22)
        schedule = RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=due_date,
            principal_due="1000.00",
            interest_due="0.00",
            charges_due="0.00",
            total_due="1000.00",
            schedule_status="pending",
        )
        captured = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/repayments/",
            data=json.dumps(
                {
                    "repayment_source": "direct_farmer",
                    "amount_received": "1000.00",
                    "received_date": "2026-06-23",
                    "payment_method": "neft",
                    "bank_reference_number": "UTR-DEFAULT-PAID-001",
                    "remarks": "Confirmed payment for the scheduled principal.",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="default-paid-capture",
            **self.auth,
        )
        self.assertEqual(captured.status_code, 200, captured.content)
        repayment_id = captured.json()["data"]["repayment_id"]
        posted = self.client.post(
            f"/api/v1/repayments/{repayment_id}/mark-sap-posted/",
            data=json.dumps(
                {
                    "sap_entry_reference": "SAP-DEFAULT-PAID-001",
                    "sap_posted_at": "2026-06-23T10:00:00Z",
                    "remarks": "Posting confirmed.",
                }
            ),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(posted.status_code, 200, posted.content)
        allocated = self.client.post(
            f"/api/v1/repayments/{repayment_id}/allocate/",
            data=json.dumps(
                {
                    "allocation_rule": "principal_first",
                    "remarks": "Apply to the due principal obligation.",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="default-paid-allocation",
            **self.auth,
        )
        self.assertEqual(allocated.status_code, 200, allocated.content)
        schedule.refresh_from_db()
        self.assertEqual(str(schedule.paid_principal), "1000.00")

        response = self.client.post(
            f"/api/v1/loan-accounts/{self.account.pk}/default-cases/open/",
            data=json.dumps(
                {
                    "trigger_event": "missed_principal_repayment",
                    "scheduled_due_date": due_date.isoformat(),
                    "reason": "A caller must not override allocation truth.",
                }
            ),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(DefaultCase.objects.count(), 0)
