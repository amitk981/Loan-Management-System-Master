# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 16414459
Lines: 356423
SHA-256: 20e684a5a67acb04de7c4dbc259210521277f61b1e1f0ee6a81181749338af25
Session ID: 019f78e1-5a69-7d62-91ee-03a31c2e5d04
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+        workflow.pk = uuid4()
+        workflow.entity_id = account.pk
+        workflow.created_at = account.created_at
+        workflow.save(force_insert=True)
+        return account.pk
+
 
 class ActiveLoanAccountReadApiTests(TestCase):
     def setUp(self):
@@ -345,6 +495,42 @@
         self.assertEqual(listing.json()["data"], [])
         self.assertEqual(listing.json()["pagination"]["total_count"], 0)
 
+    def test_member_and_account_sap_reads_reject_newer_cross_application_drift_identically(self):
+        from sfpcl_credit.sap_workflow.models import SapCustomerProfileRequest
+        from sfpcl_credit.sap_workflow.modules.sap_customer_profile import (
+            get_account_customer_code,
+            get_customer_code_for_member,
+        )
+
+        original = SapCustomerProfileRequest.objects.get(
+            loan_application_id=self.account.loan_application_id,
+            request_status=SapCustomerProfileRequest.STATUS_COMPLETED,
+        )
+        later_application = copy(original.loan_application)
+        later_application._state = copy(original.loan_application._state)
+        later_application._state.adding = True
+        later_application.pk = uuid4()
+        later_application.application_reference_number = "LO-READ-CROSS-APP"
+        later_application.created_at = original.loan_application.created_at + timedelta(days=1)
+        later_application.save(force_insert=True)
+        stale_cross_application = copy(original)
+        stale_cross_application._state = copy(original._state)
+        stale_cross_application._state.adding = True
+        stale_cross_application.pk = uuid4()
+        stale_cross_application.loan_application = later_application
+        stale_cross_application.created_at = original.created_at + timedelta(days=1)
+        stale_cross_application.save(force_insert=True)
+
+        member_decision = get_customer_code_for_member(self.account.member_id)
+        account_decision = get_account_customer_code(
+            application_id=self.account.loan_application_id,
+            member_id=self.account.member_id,
+            customer_code_id=self.account.sap_customer_code_id,
+        )
+
+        self.assertIsNone(member_decision)
+        self.assertIsNone(account_decision)
+
     def test_exact_active_scope_allows_assigned_finance_cfc_and_credit(self):
         finance = self.fixture.owner.fixture.actor
         cfc = self.fixture.actor

tokens used
563,060
Ralph run stopped after three independent review rounds retained High-severity blockers. This attempt must not be validated or committed.

What is green:

- Canonical member/account SAP decision and cross-application drift regression.
- Lifecycle-owned creation selector with bounded bulk evidence reconciliation.
- Database pagination across all workspace branches.
- Correct combined S37/Loan Account offset arithmetic.
- Mutation-owner predicates for CFC authorisation, transfer success, and advice actions.
- Loan Account pagination tests at full-page, 21-row, and 101-row scales.
- MP14 explicit-ID selection tests in both list orders.
- Backend focused validation: 110 passed, 7 skipped.
- CFC workspace/authorisation validation: 25 passed, 2 skipped.
- Frontend: 6 tests, typecheck, lint, and build passed.
- Django checks and migration synchronization passed.
- No protected or source files were modified.

Blocking findings:

- Loan Account SAP and post-transfer counts can still include identities rejected by exact evidence checks after pagination.
- Assigned S37 and CFC counts have the same count-before-exact-reconciliation defect.
- Consequently, totals, page reachability, and offsets are not guaranteed truthful under evidence corruption.
- The required mixed 1/21/101 staff-workspace acceptance and query-ceiling matrix remains incomplete.

The run artifacts record the failure and direct Ralph to use its one repair attempt. `review-packet.md` was intentionally not marked “Ready for independent validation,” so the workflow fails closed.
