import json
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase


class RepaymentAllocationApiTests(TestCase):
    def setUp(self):
        from sfpcl_credit.tests.test_direct_repayment_posting_api import (
            DirectRepaymentPostingApiTests,
        )

        fixture = DirectRepaymentPostingApiTests(
            "test_valid_direct_receipt_and_exact_replay_create_one_pending_obligation"
        )
        fixture.setUp()
        self.fixture = fixture
        self.account = fixture.account
        self.actor = fixture.actor
        fixture.fixture.fixture.owner.fixture.fixture._grant(
            self.actor, "finance.repayment.allocate"
        )
        self.client = Client()
        self.auth = fixture.fixture.fixture.owner.fixture._auth(self.actor)

    def test_partial_receipt_reduces_principal_and_appends_immutable_evidence(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import LoanAccount, Repayment, RepaymentAllocation

        captured = self.fixture._capture(self.fixture._payload(), "allocation-partial")
        repayment_id = captured.json()["data"]["repayment_id"]
        self._schedule("400000.00")

        allocated = self._allocate(repayment_id)

        self.assertEqual(allocated.status_code, 200, allocated.content)
        allocation = RepaymentAllocation.objects.get(repayment_id=repayment_id)
        account = LoanAccount.objects.get(pk=self.account.pk)
        repayment = Repayment.objects.get(pk=repayment_id)
        self.assertEqual(str(allocation.allocated_to_principal), "100000.00")
        self.assertEqual(str(allocation.allocated_to_interest), "0.00")
        self.assertEqual(str(allocation.allocated_to_charges), "0.00")
        self.assertEqual(str(allocation.unallocated_amount), "0.00")
        self.assertEqual(str(account.principal_outstanding), "300000.00")
        self.assertEqual(str(account.interest_outstanding), "0.00")
        self.assertEqual(str(account.total_outstanding), "300000.00")
        self.assertEqual(repayment.allocation_status, "allocated")
        self.assertEqual(AuditLog.objects.filter(action="repayment.allocated").count(), 1)
        self.assertEqual(
            allocated.json()["data"],
            {
                "repayment_allocation_id": str(allocation.pk),
                "repayment_id": repayment_id,
                "allocation_rule": "principal_first",
                "allocation_rule_version": "v1",
                "allocation_status": "allocated",
                "allocated_to_principal": "100000.00",
                "allocated_to_interest": "0.00",
                "allocated_to_charges": "0.00",
                "unallocated_amount": "0.00",
                "exception_reason": None,
                "loan_account": {
                    "principal_outstanding": "300000.00",
                    "interest_outstanding": "0.00",
                    "charges_outstanding": "0.00",
                    "total_outstanding": "300000.00",
                },
            },
        )

        ledger = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/ledger/", **self.auth
        )
        self.assertEqual(ledger.status_code, 200, ledger.content)
        self.assertEqual(ledger.json()["pagination"]["total_count"], 2)
        repayment_row = ledger.json()["data"][1]
        self.assertEqual(repayment_row["transaction_type"], "repayment")
        self.assertEqual(repayment_row["credit"], "100000.00")
        self.assertEqual(repayment_row["principal_balance"], "300000.00")
        self.assertEqual(repayment_row["total_outstanding"], "300000.00")

    def test_crossing_receipt_updates_schedule_then_retains_charges_and_excess(self):
        from sfpcl_credit.loans.models import LoanAccount, RepaymentAllocation, RepaymentSchedule

        LoanAccount.objects.filter(pk=self.account.pk).update(
            principal_outstanding="40000.00",
            interest_outstanding="10000.00",
            charges_outstanding="5000.00",
            total_outstanding="55000.00",
        )
        schedule = RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=self.account.repayment_date + timedelta(days=1),
            principal_due="40000.00",
            interest_due="10000.00",
            charges_due="5000.00",
            total_due="55000.00",
            schedule_status="pending",
        )
        payload = {
            **self.fixture._payload(),
            "amount_received": "60000.00",
            "bank_reference_number": "UTR-ALLOCATION-CROSSING",
        }
        captured = self.fixture._capture(payload, "allocation-crossing")

        response = self._allocate(captured.json()["data"]["repayment_id"])

        self.assertEqual(response.status_code, 200, response.content)
        allocation = RepaymentAllocation.objects.get()
        account = LoanAccount.objects.get(pk=self.account.pk)
        schedule.refresh_from_db()
        self.assertEqual(str(allocation.allocated_to_principal), "40000.00")
        self.assertEqual(str(allocation.allocated_to_interest), "10000.00")
        self.assertEqual(str(allocation.allocated_to_charges), "0.00")
        self.assertEqual(str(allocation.unallocated_amount), "10000.00")
        self.assertEqual(allocation.exception_reason, "charge_or_excess_policy_not_configured")
        self.assertEqual(str(account.principal_outstanding), "0.00")
        self.assertEqual(str(account.interest_outstanding), "0.00")
        self.assertEqual(str(account.charges_outstanding), "5000.00")
        self.assertEqual(str(account.total_outstanding), "5000.00")
        self.assertEqual(str(schedule.paid_principal), "40000.00")
        self.assertEqual(str(schedule.paid_interest), "10000.00")
        self.assertEqual(str(schedule.paid_charges), "0.00")
        self.assertEqual(schedule.schedule_status, "pending")
        self.assertEqual(response.json()["data"]["allocation_status"], "allocated_with_exception")

    def test_exact_payoff_replay_returns_retained_truth_with_one_financial_effect(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import (
            LoanAccount,
            Repayment,
            RepaymentAllocation,
            RepaymentLedgerEntry,
            RepaymentSapPostingObligation,
        )

        payload = {
            **self.fixture._payload(),
            "amount_received": "400000.00",
            "bank_reference_number": "UTR-ALLOCATION-PAYOFF",
        }
        captured = self.fixture._capture(payload, "allocation-payoff")
        repayment_id = captured.json()["data"]["repayment_id"]
        self._schedule("400000.00")
        self._ensure_posted(repayment_id)
        capture_truth = (
            Repayment.objects.values().get(pk=repayment_id),
            RepaymentSapPostingObligation.objects.values().get(repayment_id=repayment_id),
        )

        first = self._allocate(repayment_id)
        replay = self._allocate(repayment_id)
        changed = self._allocate(
            repayment_id,
            payload={
                "allocation_rule": "principal_first",
                "remarks": "Changed replay must not reuse retained truth.",
            },
        )

        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(changed.status_code, 409, changed.content)
        self.assertEqual(
            replay.json()["data"],
            {
                "idempotency_replayed": True,
                "original_response": first.json()["data"],
            },
        )
        account = LoanAccount.objects.get(pk=self.account.pk)
        self.assertEqual(str(account.principal_outstanding), "0.00")
        self.assertEqual(str(account.total_outstanding), "0.00")
        self.assertEqual(account.loan_account_status, "repaid")
        self.assertEqual(RepaymentAllocation.objects.count(), 1)
        self.assertEqual(RepaymentLedgerEntry.objects.count(), 1)
        self.assertEqual(AuditLog.objects.filter(action="repayment.allocated").count(), 1)
        repayment = Repayment.objects.values().get(pk=repayment_id)
        obligation = RepaymentSapPostingObligation.objects.values().get(repayment_id=repayment_id)
        self.assertEqual(
            {key: value for key, value in repayment.items() if key != "allocation_status"},
            {key: value for key, value in capture_truth[0].items() if key != "allocation_status"},
        )
        self.assertEqual(obligation, capture_truth[1])

    def test_replay_after_later_status_change_returns_frozen_original_response(self):
        from sfpcl_credit.loans.models import Repayment, RepaymentAllocation

        captured = self.fixture._capture(
            self.fixture._payload(), "allocation-frozen-replay"
        )
        repayment_id = captured.json()["data"]["repayment_id"]
        self._schedule("400000.00")
        first = self._allocate(repayment_id)
        self.assertEqual(first.status_code, 200, first.content)
        Repayment.objects.filter(pk=repayment_id).update(
            allocation_status="reversed"
        )

        replay = self._allocate(repayment_id)

        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(
            replay.json()["data"],
            {
                "idempotency_replayed": True,
                "original_response": first.json()["data"],
            },
        )
        self.assertEqual(RepaymentAllocation.objects.count(), 1)

    def test_incoherent_capture_evidence_is_zero_write_conflict(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import LoanAccount, RepaymentAllocation, RepaymentLedgerEntry

        captured = self.fixture._capture(self.fixture._payload(), "allocation-drifted-capture")
        repayment_id = captured.json()["data"]["repayment_id"]
        repayment_audit = AuditLog.objects.get(action="repayment.receipt_created")
        AuditLog.objects.filter(pk=repayment_audit.pk).update(action="repayment.receipt_changed")
        account_before = LoanAccount.objects.values().get(pk=self.account.pk)

        response = self._allocate(repayment_id)

        self.assertEqual(response.status_code, 409, response.content)
        self.assertEqual(RepaymentAllocation.objects.count(), 0)
        self.assertEqual(RepaymentLedgerEntry.objects.count(), 0)
        self.assertEqual(LoanAccount.objects.values().get(pk=self.account.pk), account_before)
        self.assertEqual(AuditLog.objects.filter(action="repayment.allocated").count(), 0)

    def test_allocation_requires_valid_input_authority_and_object_scope(self):
        from uuid import uuid4

        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import LoanAccount, RepaymentAllocation, RepaymentLedgerEntry

        captured = self.fixture._capture(self.fixture._payload(), "allocation-authority")
        repayment_id = captured.json()["data"]["repayment_id"]
        user_fixture = self.fixture.fixture.fixture.owner.fixture.fixture
        auth_fixture = self.fixture.fixture.fixture.owner.fixture
        role_only = user_fixture._user("cfo", "Allocation Unauthorised Role")
        permission_only = user_fixture._user("field_officer", "Allocation Permission Only")
        scoped_actor = user_fixture._user("credit_manager", "Scoped Allocation Actor")
        user_fixture._grant(permission_only, "finance.repayment.allocate")
        user_fixture._grant(scoped_actor, "finance.repayment.allocate")

        cases = (
            ({}, 401),
            (auth_fixture._auth(role_only), 403),
            (auth_fixture._auth(permission_only), 403),
        )
        for auth, expected in cases:
            with self.subTest(expected=expected):
                response = self._allocate(repayment_id, auth=auth)
                self.assertEqual(response.status_code, expected, response.content)
                self.assertEqual(RepaymentAllocation.objects.count(), 0)
                self.assertEqual(RepaymentLedgerEntry.objects.count(), 0)

        invalid = self._allocate(
            repayment_id,
            payload={"allocation_rule": "interest_first", "remarks": " "},
        )
        self.assertEqual(invalid.status_code, 400, invalid.content)
        self.assertEqual(RepaymentAllocation.objects.count(), 0)

        account_before = LoanAccount.objects.values().get(pk=self.account.pk)
        LoanAccount.objects.filter(pk=self.account.pk).update(loan_account_status="closed")
        scoped_auth = auth_fixture._auth(scoped_actor)
        inaccessible = self._allocate(repayment_id, auth=scoped_auth)
        missing = self._allocate(uuid4(), auth=scoped_auth)
        self.assertEqual(inaccessible.status_code, 404, inaccessible.content)
        self.assertEqual(missing.status_code, 404, missing.content)
        self.assertEqual(RepaymentAllocation.objects.count(), 0)
        self.assertEqual(RepaymentLedgerEntry.objects.count(), 0)
        self.assertEqual(AuditLog.objects.filter(action="repayment.allocated").count(), 0)
        account_after = LoanAccount.objects.values().get(pk=self.account.pk)
        self.assertEqual(
            {key: value for key, value in account_after.items() if key != "loan_account_status"},
            {key: value for key, value in account_before.items() if key != "loan_account_status"},
        )

    def test_database_enforces_balance_arithmetic_and_evidence_is_append_only(self):
        from sfpcl_credit.loans.models import (
            RepaymentAllocation,
            RepaymentLedgerEntry,
            RepaymentSchedule,
        )

        schedule = RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=self.account.repayment_date,
            principal_due="400000.00",
            interest_due="0.00",
            charges_due="0.00",
            total_due="400000.00",
            schedule_status="pending",
        )
        captured = self.fixture._capture(self.fixture._payload(), "allocation-db-rules")
        response = self._allocate(captured.json()["data"]["repayment_id"])
        self.assertEqual(response.status_code, 200, response.content)
        allocation = RepaymentAllocation.objects.get()
        ledger = RepaymentLedgerEntry.objects.get()

        with self.assertRaises(IntegrityError), transaction.atomic():
            RepaymentAllocation._base_manager.filter(pk=allocation.pk).update(
                principal_after="299999.00"
            )
        with self.assertRaises(IntegrityError), transaction.atomic():
            RepaymentLedgerEntry._base_manager.filter(pk=ledger.pk).update(
                total_outstanding="299999.00"
            )
        with self.assertRaises(IntegrityError), transaction.atomic():
            RepaymentSchedule._base_manager.filter(pk=schedule.pk).update(
                paid_principal="400000.01"
            )
        allocation.exception_reason = "changed"
        ledger.actor_display_name = "Changed"
        for mutation in (
            lambda: allocation.save(),
            lambda: allocation.delete(),
            lambda: ledger.save(),
            lambda: ledger.delete(),
            lambda: RepaymentAllocation.objects.filter(pk=allocation.pk).update(
                exception_reason="changed"
            ),
        ):
            with self.assertRaises(ValidationError):
                mutation()

    def _allocate(self, repayment_id, payload=None, auth=None):
        self._ensure_posted(repayment_id)
        return self.client.post(
            f"/api/v1/repayments/{repayment_id}/allocate/",
            data=json.dumps(
                payload
                or {
                    "allocation_rule": "principal_first",
                    "remarks": "Allocate confirmed receipt under the approved SOP.",
                }
            ),
            content_type="application/json",
            HTTP_X_REQUEST_ID="req-allocation-001",
            HTTP_USER_AGENT="allocation contract test",
            REMOTE_ADDR="203.0.113.51",
            HTTP_IDEMPOTENCY_KEY=f"allocation-{repayment_id}",
            **(self.auth if auth is None else auth),
        )

    def _ensure_posted(self, repayment_id):
        from sfpcl_credit.loans.models import Repayment

        repayment = Repayment.objects.filter(pk=repayment_id).first()
        if repayment is not None and repayment.sap_posting_status == "pending":
            response = self.fixture._mark(
                repayment_id,
                {
                    "sap_entry_reference": f"SAP-{repayment_id}",
                    "sap_posted_at": "2026-12-05T10:00:00Z",
                    "remarks": "Posting confirmed before allocation.",
                },
            )
            self.assertEqual(response.status_code, 200, response.content)

    def _schedule(self, principal):
        from sfpcl_credit.loans.models import RepaymentSchedule

        return RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=self.account.repayment_date,
            principal_due=principal,
            interest_due="0.00",
            charges_due="0.00",
            total_due=principal,
            schedule_status="pending",
        )
