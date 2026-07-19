import json
import tempfile
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import close_old_connections, connection
from django.test import Client, TestCase, TransactionTestCase, override_settings


@override_settings(DOCUMENT_STORAGE_ROOT=tempfile.mkdtemp(prefix="sfpcl-adjustment-tests-"))
class RepaymentAdjustmentApiTests(TestCase):
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

    def test_allocation_requires_posted_sap_decision_and_idempotency_key(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import (
            LoanAccount, Repayment, RepaymentAllocation, RepaymentLedgerEntry,
        )

        self._full_schedule()
        captured = self.fixture._capture(
            self.fixture._payload(), "adjustment-admission-receipt"
        )
        repayment_id = captured.json()["data"]["repayment_id"]
        before = self._financial_truth()

        pending = self._allocate(repayment_id, key="adjustment-admission")
        missing_key = self._allocate(repayment_id, key="")

        self.assertEqual(pending.status_code, 409, pending.content)
        self.assertEqual(missing_key.status_code, 400, missing_key.content)
        self.assertEqual(self._financial_truth(), before)

        posted = self.fixture._mark(
            repayment_id,
            {
                "sap_entry_reference": "SAP-ADMISSION-001",
                "sap_posted_at": "2026-12-05T10:00:00Z",
                "remarks": "Posting confirmed.",
            },
        )
        self.assertEqual(posted.status_code, 200, posted.content)
        allocated = self._allocate(repayment_id, key="adjustment-admission")
        self.assertEqual(allocated.status_code, 200, allocated.content)
        self.assertEqual(RepaymentAllocation.objects.count(), 1)
        self.assertEqual(RepaymentLedgerEntry.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="repayment.allocated").count(), 1
        )
        self.assertEqual(
            Repayment.objects.get(pk=repayment_id).allocation_status, "allocated"
        )
        self.assertEqual(
            str(LoanAccount.objects.get(pk=self.account.pk).principal_outstanding),
            "300000.00",
        )

    def test_allocation_fails_closed_when_schedule_cannot_absorb_exact_amount(self):
        from datetime import timedelta

        from sfpcl_credit.loans.models import RepaymentSchedule

        repayment_id = self._capture_and_post("schedule-capacity-receipt")
        before = self._financial_truth()

        empty = self._allocate(repayment_id, key="schedule-capacity-empty")

        self.assertEqual(empty.status_code, 409, empty.content)
        self.assertEqual(self._financial_truth(), before)

        for number in range(1, 22):
            RepaymentSchedule.objects.create(
                loan_account=self.account,
                installment_number=number,
                due_date=self.account.repayment_date + timedelta(days=number),
                principal_due="4000.00",
                interest_due="0.00",
                charges_due="0.00",
                total_due="4000.00",
                schedule_status="pending",
            )
        insufficient_before = self._financial_truth()
        insufficient = self._allocate(
            repayment_id, key="schedule-capacity-insufficient"
        )
        self.assertEqual(insufficient.status_code, 409, insufficient.content)
        self.assertEqual(self._financial_truth(), insufficient_before)

        RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=22,
            due_date=self.account.repayment_date + timedelta(days=22),
            principal_due="16000.00",
            interest_due="0.00",
            charges_due="0.00",
            total_due="16000.00",
            schedule_status="pending",
        )
        allocated = self._allocate(repayment_id, key="schedule-capacity-exact")
        self.assertEqual(allocated.status_code, 200, allocated.content)
        self.assertEqual(
            f"{sum(line.paid_principal for line in RepaymentSchedule.objects.all()):.2f}",
            self.fixture._payload()["amount_received"],
        )

    def test_manual_exception_allocation_requires_exact_terminal_approval(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import RepaymentAllocation, RepaymentSchedule

        self._full_schedule()
        repayment_id = self._manual_exception_receipt()
        before = self._financial_truth()

        ordinary = self._allocate(repayment_id, key="manual-ordinary-denied")
        missing_approval = self._manual_allocate(
            repayment_id, approval_id="00000000-0000-0000-0000-000000000000"
        )
        approval_denied = self._approve_manual(repayment_id)

        self.assertEqual(ordinary.status_code, 409, ordinary.content)
        self.assertEqual(missing_approval.status_code, 409, missing_approval.content)
        self.assertEqual(approval_denied.status_code, 403, approval_denied.content)
        self.assertEqual(self._financial_truth(), before)

        self.fixture.fixture.fixture.owner.fixture.fixture._grant(
            self.actor, "finance.repayment.manual_allocation_approve"
        )
        drifted_approval = self._approve_manual(
            repayment_id,
            amount="99999.00",
            key="manual-adjustment-approval-drift",
        )
        self.assertEqual(drifted_approval.status_code, 409, drifted_approval.content)
        approved = self._approve_manual(repayment_id)
        self.assertEqual(approved.status_code, 200, approved.content)
        approval_id = approved.json()["data"]["manual_allocation_approval_id"]

        allocated = self._manual_allocate(repayment_id, approval_id=approval_id)
        replay = self._manual_allocate(repayment_id, approval_id=approval_id)
        self.assertEqual(allocated.status_code, 200, allocated.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], allocated.json()["data"])
        allocation = RepaymentAllocation.objects.get()
        self.assertEqual(str(allocation.manual_approval_id), approval_id)
        self.assertEqual(str(allocation.allocated_to_principal), "100000.00")
        approval_audit = AuditLog.objects.get(
            action="repayment.manual_allocation_approved"
        )
        self.assertNotIn("Approve the exact retained", str(approval_audit.new_value_json))
        self.assertNotIn("UNKNOWN-MANUAL", str(approval_audit.new_value_json))

    def test_reversal_appends_compensating_truth_and_preserves_original_rows(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import (
            LoanAccount, RepaymentAllocation, RepaymentLedgerEntry, RepaymentReversal,
            RepaymentReversalLedgerEntry,
        )

        schedule = self._full_schedule()
        repayment_id = self._capture_and_post("reversal-receipt")
        allocated = self._allocate(repayment_id, key="reversal-allocation")
        self.assertEqual(allocated.status_code, 200, allocated.content)
        allocation = RepaymentAllocation.objects.values().get()
        ledger = RepaymentLedgerEntry.objects.values().get()

        denied = self._reverse(repayment_id, key="reversal-action")
        self.assertEqual(denied.status_code, 403, denied.content)
        self.assertEqual(RepaymentReversal.objects.count(), 0)

        self.fixture.fixture.fixture.owner.fixture.fixture._grant(
            self.actor, "finance.repayment.reverse"
        )
        reversed_response = self._reverse(repayment_id, key="reversal-action")
        replay = self._reverse(repayment_id, key="reversal-action")
        changed = self._reverse(
            repayment_id,
            key="reversal-action",
            reason="A changed request must never replay.",
        )

        self.assertEqual(reversed_response.status_code, 200, reversed_response.content)
        self.assertEqual(replay.status_code, 200, replay.content)
        self.assertEqual(replay.json()["data"], reversed_response.json()["data"])
        self.assertEqual(changed.status_code, 409, changed.content)
        self.assertEqual(RepaymentReversal.objects.count(), 1)
        self.assertEqual(RepaymentReversalLedgerEntry.objects.count(), 1)
        self.assertEqual(
            AuditLog.objects.filter(action="repayment.reversed").count(), 1
        )
        reversal_audit = AuditLog.objects.get(action="repayment.reversed")
        self.assertNotIn("Correct the erroneous", str(reversal_audit.new_value_json))
        self.assertNotIn("UTR-DIRECT", str(reversal_audit.new_value_json))
        self.assertEqual(RepaymentAllocation.objects.values().get(), allocation)
        self.assertEqual(RepaymentLedgerEntry.objects.values().get(), ledger)
        account = LoanAccount.objects.get(pk=self.account.pk)
        schedule.refresh_from_db()
        self.assertEqual(str(account.principal_outstanding), "400000.00")
        self.assertEqual(str(account.total_outstanding), "400000.00")
        self.assertEqual(account.loan_account_status, "active")
        self.assertEqual(str(schedule.paid_principal), "0.00")
        self.assertEqual(schedule.schedule_status, "pending")
        ledger_response = self.client.get(
            f"/api/v1/loan-accounts/{self.account.pk}/ledger/", **self.auth
        )
        self.assertEqual(ledger_response.status_code, 200, ledger_response.content)
        self.assertEqual(
            [row["transaction_type"] for row in ledger_response.json()["data"]],
            ["disbursement", "repayment", "reversal"],
        )
        self.assertEqual(ledger_response.json()["data"][2]["debit"], "100000.00")

    def _financial_truth(self):
        from sfpcl_credit.identity.models import AuditLog
        from sfpcl_credit.loans.models import (
            LoanAccount, Repayment, RepaymentAllocation, RepaymentLedgerEntry,
            RepaymentSchedule,
        )

        return {
            "account": LoanAccount.objects.values().get(pk=self.account.pk),
            "repayments": list(Repayment.objects.values()),
            "schedules": list(RepaymentSchedule.objects.values()),
            "allocations": list(RepaymentAllocation.objects.values()),
            "ledger": list(RepaymentLedgerEntry.objects.values()),
            "financial_audits": list(
                AuditLog.objects.filter(
                    action__in=("repayment.allocated", "repayment.reversed")
                ).values()
            ),
        }

    def _allocate(self, repayment_id, *, key, payload=None):
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
            HTTP_IDEMPOTENCY_KEY=key,
            HTTP_X_REQUEST_ID="req-adjustment-allocation",
            **self.auth,
        )

    def _capture_and_post(self, key):
        captured = self.fixture._capture(self.fixture._payload(), key)
        repayment_id = captured.json()["data"]["repayment_id"]
        posted = self.fixture._mark(
            repayment_id,
            {
                "sap_entry_reference": f"SAP-{key}",
                "sap_posted_at": "2026-12-05T10:00:00Z",
                "remarks": "Posting confirmed.",
            },
        )
        self.assertEqual(posted.status_code, 200, posted.content)
        return repayment_id

    def _manual_exception_receipt(self):
        from sfpcl_credit.configurations.modules.source_bank_governance import (
            resolve_source_bank_account,
        )

        self.fixture.fixture.fixture.owner.fixture.fixture._grant(
            self.actor,
            "finance.bank_statement.read",
            "finance.bank_statement.import",
            "finance.bank_statement.match",
        )
        repayment_id = self._capture_and_post("manual-adjustment-receipt")
        content = (
            "transaction_date,value_date,amount,narration,reference,loan_account_number\n"
            f"2026-12-04,2026-12-04,100000.00,Manual exception,UNKNOWN-MANUAL,"
            f"{self.account.loan_account_number}\n"
        )
        imported = self.client.post(
            "/api/v1/bank-statement-imports/",
            data={
                "file": SimpleUploadedFile(
                    "manual.csv", content.encode(), content_type="text/csv"
                ),
                "collection_bank_account_id": str(
                    resolve_source_bank_account().source_bank_account_id
                ),
            },
            HTTP_IDEMPOTENCY_KEY="manual-adjustment-statement",
            **self.auth,
        )
        self.assertEqual(imported.status_code, 200, imported.content)
        line_id = imported.json()["data"]["lines"][0]["bank_statement_line_id"]
        matched = self.client.post(
            f"/api/v1/bank-statement-lines/{line_id}/match/",
            data=json.dumps(
                {
                    "repayment_id": repayment_id,
                    "reason": "Automatic matching failed; retained evidence was reviewed.",
                }
            ),
            content_type="application/json",
            **self.auth,
        )
        self.assertEqual(matched.status_code, 200, matched.content)
        return repayment_id

    def _approve_manual(
        self,
        repayment_id,
        *,
        amount="100000.00",
        key="manual-adjustment-approval",
    ):
        return self.client.post(
            f"/api/v1/repayments/{repayment_id}/manual-allocation-approvals/",
            data=json.dumps(
                {
                    "loan_account_id": str(self.account.pk),
                    "amount": amount,
                    "reason": "Approve the exact retained exception allocation.",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=key,
            **self.auth,
        )

    def _manual_allocate(self, repayment_id, *, approval_id):
        return self.client.post(
            f"/api/v1/repayments/{repayment_id}/manual-allocate/",
            data=json.dumps(
                {
                    "approval_id": approval_id,
                    "allocation_rule": "principal_first",
                    "remarks": "Apply the approved exception allocation.",
                }
            ),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY="manual-adjustment-allocation",
            **self.auth,
        )

    def _reverse(self, repayment_id, *, key, reason="Correct the erroneous posting."):
        return self.client.post(
            f"/api/v1/repayments/{repayment_id}/reverse/",
            data=json.dumps({"reason": reason}),
            content_type="application/json",
            HTTP_IDEMPOTENCY_KEY=key,
            HTTP_X_REQUEST_ID="req-adjustment-reversal",
            **self.auth,
        )

    def _full_schedule(self):
        from sfpcl_credit.loans.models import RepaymentSchedule

        return RepaymentSchedule.objects.create(
            loan_account=self.account,
            installment_number=1,
            due_date=self.account.repayment_date,
            principal_due="400000.00",
            interest_due="0.00",
            charges_due="0.00",
            total_due="400000.00",
            schedule_status="pending",
        )


class RepaymentAdjustmentCatalogueTests(TestCase):
    def test_default_role_catalogue_grants_only_source_allocation_authority(self):
        from sfpcl_credit.identity.catalogue import seed_catalogue
        from sfpcl_credit.identity.models import RolePermission

        seed_catalogue()
        grants = {
            code: set(
                RolePermission.objects.filter(
                    permission__permission_code=code
                ).values_list("role__role_code", flat=True)
            )
            for code in (
                "finance.repayment.create",
                "finance.repayment.allocate",
                "finance.repayment.manual_allocation_approve",
                "finance.repayment.reverse",
            )
        }
        self.assertEqual(
            grants["finance.repayment.create"], {"credit_manager", "accounts_head"}
        )
        self.assertEqual(
            grants["finance.repayment.allocate"], {"credit_manager", "accounts_head"}
        )
        self.assertEqual(grants["finance.repayment.manual_allocation_approve"], set())
        self.assertEqual(grants["finance.repayment.reverse"], set())


@skipUnless(connection.vendor == "postgresql", "PostgreSQL financial acceptance")
class RepaymentAdjustmentPostgreSQLAcceptanceTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.fixture = RepaymentAdjustmentApiTests(
            "test_allocation_requires_posted_sap_decision_and_idempotency_key"
        )
        self.fixture.setUp()

    def test_concurrent_allocation_exact_replay_retains_one_financial_effect(self):
        from sfpcl_credit.loans.models import RepaymentAllocation, RepaymentLedgerEntry

        self._full_schedule()
        repayment_id = self.fixture._capture_and_post("pg-allocation-receipt")
        statuses = self._race(
            f"/api/v1/repayments/{repayment_id}/allocate/",
            {
                "allocation_rule": "principal_first",
                "remarks": "Concurrent exact allocation.",
            },
            key="pg-allocation-key",
        )
        self.assertEqual(statuses, [200, 200])
        self.assertEqual(RepaymentAllocation.objects.count(), 1)
        self.assertEqual(RepaymentLedgerEntry.objects.count(), 1)

    def test_concurrent_reversal_exact_replay_retains_one_compensating_effect(self):
        from sfpcl_credit.loans.models import RepaymentReversal, RepaymentReversalLedgerEntry

        self._full_schedule()
        repayment_id = self.fixture._capture_and_post("pg-reversal-receipt")
        allocated = self.fixture._allocate(repayment_id, key="pg-reversal-allocation")
        self.assertEqual(allocated.status_code, 200, allocated.content)
        self.fixture.fixture.fixture.fixture.owner.fixture.fixture._grant(
            self.fixture.actor, "finance.repayment.reverse"
        )
        statuses = self._race(
            f"/api/v1/repayments/{repayment_id}/reverse/",
            {"reason": "Concurrent exact reversal."},
            key="pg-reversal-key",
        )
        self.assertEqual(statuses, [200, 200])
        self.assertEqual(RepaymentReversal.objects.count(), 1)
        self.assertEqual(RepaymentReversalLedgerEntry.objects.count(), 1)

    def test_one_hundred_one_schedule_rows_reconcile_exactly(self):
        from datetime import timedelta

        from sfpcl_credit.loans.models import RepaymentSchedule

        for number in range(1, 102):
            amount = "990.00" if number <= 100 else "1000.00"
            RepaymentSchedule.objects.create(
                loan_account=self.fixture.account,
                installment_number=number,
                due_date=self.fixture.account.repayment_date + timedelta(days=number),
                principal_due=amount,
                interest_due="0.00",
                charges_due="0.00",
                total_due=amount,
                schedule_status="pending",
            )
        repayment_id = self.fixture._capture_and_post("pg-101-receipt")
        response = self.fixture._allocate(repayment_id, key="pg-101-allocation")
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            f"{sum(row.paid_principal for row in RepaymentSchedule.objects.all()):.2f}",
            "100000.00",
        )

    def test_cross_receipt_idempotency_reuse_is_zero_write_conflict(self):
        from sfpcl_credit.loans.models import RepaymentAllocation

        self._full_schedule()
        first_id = self.fixture._capture_and_post("pg-cross-first")
        second = self.fixture.fixture._capture(
            {
                **self.fixture.fixture._payload(),
                "bank_reference_number": "UTR-PG-CROSS-SECOND",
            },
            "pg-cross-second",
        )
        second_id = second.json()["data"]["repayment_id"]
        self.fixture.fixture._mark(
            second_id,
            {
                "sap_entry_reference": "SAP-PG-CROSS-SECOND",
                "sap_posted_at": "2026-12-05T10:00:00Z",
                "remarks": "Posting confirmed.",
            },
        )
        first = self.fixture._allocate(first_id, key="pg-cross-key")
        cross = self.fixture._allocate(second_id, key="pg-cross-key")
        self.assertEqual(first.status_code, 200, first.content)
        self.assertEqual(cross.status_code, 409, cross.content)
        self.assertEqual(RepaymentAllocation.objects.count(), 1)

    def _race(self, url, payload, *, key):
        barrier = Barrier(2)

        def submit(_):
            close_old_connections()
            barrier.wait()
            response = Client().post(
                url,
                data=json.dumps(payload),
                content_type="application/json",
                HTTP_IDEMPOTENCY_KEY=key,
                **self.fixture.auth,
            )
            close_old_connections()
            return response.status_code

        with ThreadPoolExecutor(max_workers=2) as pool:
            return sorted(pool.map(submit, range(2)))

    def _full_schedule(self):
        from sfpcl_credit.loans.models import RepaymentSchedule

        return RepaymentSchedule.objects.create(
            loan_account=self.fixture.account,
            installment_number=1,
            due_date=self.fixture.account.repayment_date,
            principal_due="400000.00",
            interest_due="0.00",
            charges_due="0.00",
            total_due="400000.00",
            schedule_status="pending",
        )
