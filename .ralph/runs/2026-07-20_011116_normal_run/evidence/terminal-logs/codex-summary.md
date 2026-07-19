# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 18889621
Lines: 400335
SHA-256: 959f642d7effcf47c390158a756d6c9c1850bd5595a96e262cb503362453eb7f
Session ID: 019f7be5-e7b4-7da1-b361-95fd7b1a6841
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

@@ -272,7 +283,7 @@
             )
         with self.assertRaises(IntegrityError), transaction.atomic():
             RepaymentSchedule._base_manager.filter(pk=schedule.pk).update(
-                paid_principal="1000.01"
+                paid_principal="400000.01"
             )
         allocation.exception_reason = "changed"
         ledger.actor_display_name = "Changed"
@@ -289,6 +300,7 @@
                 mutation()
 
     def _allocate(self, repayment_id, payload=None, auth=None):
+        self._ensure_posted(repayment_id)
         return self.client.post(
             f"/api/v1/repayments/{repayment_id}/allocate/",
             data=json.dumps(
@@ -302,5 +314,35 @@
             HTTP_X_REQUEST_ID="req-allocation-001",
             HTTP_USER_AGENT="allocation contract test",
             REMOTE_ADDR="203.0.113.51",
+            HTTP_IDEMPOTENCY_KEY=f"allocation-{repayment_id}",
             **(self.auth if auth is None else auth),
         )
+
+    def _ensure_posted(self, repayment_id):
+        from sfpcl_credit.loans.models import Repayment
+
+        repayment = Repayment.objects.filter(pk=repayment_id).first()
+        if repayment is not None and repayment.sap_posting_status == "pending":
+            response = self.fixture._mark(
+                repayment_id,
+                {
+                    "sap_entry_reference": f"SAP-{repayment_id}",
+                    "sap_posted_at": "2026-12-05T10:00:00Z",
+                    "remarks": "Posting confirmed before allocation.",
+                },
+            )
+            self.assertEqual(response.status_code, 200, response.content)
+
+    def _schedule(self, principal):
+        from sfpcl_credit.loans.models import RepaymentSchedule
+
+        return RepaymentSchedule.objects.create(
+            loan_account=self.account,
+            installment_number=1,
+            due_date=self.account.repayment_date,
+            principal_due=principal,
+            interest_due="0.00",
+            charges_due="0.00",
+            total_due=principal,
+            schedule_status="pending",
+        )

tokens used
403,496
Implemented slice `010C2-manual-allocation-and-financial-reversal-controls` and prepared it for Ralph’s independent validation.

Delivered:

- Posted-SAP admission and idempotency enforcement for ordinary allocation.
- Exact schedule-capacity reconciliation with immutable per-schedule application evidence.
- Governed manual allocation requiring exact terminal approval for a 010D exception.
- Atomic, append-only financial reversal with compensating ledger entries.
- Source-correct Credit Manager and Accounts capture/allocation grants.
- Default-denied manual-approval and reversal permissions.
- One additive migration and updated API contracts.
- Architecture finding closure evidence for `AR-010-ALLOCATION-001` and `AC-ALLOC-1` through `AC-ALLOC-6`.

Validation completed:

- 62 focused reverse-consumer/catalogue tests passed.
- Four-test PostgreSQL acceptance class passed twice without skips.
- `manage.py check` passed.
- Migration synchronization passed.
- `git diff --check` passed.
- No protected files were modified.
- Estimated product change: 1,991 lines, within the 2,000-line limit.

The review packet result is exactly `Ready for independent validation`. The authoritative complete backend coverage/full-suite remains for the orchestrator, as required. No Git staging, commit, merge, or push was performed.
