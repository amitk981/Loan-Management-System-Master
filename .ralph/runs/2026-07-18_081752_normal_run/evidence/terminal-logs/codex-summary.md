# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 7397639
Lines: 163272
SHA-256: 06fe62a599d8d3809f0b583a0e014c4ab3aad764eb9ff816082c913c1c0539cd
Session ID: 019f731f-d8ca-7ad3-a619-e065527c07f7
Raw retention: operator-local, at most 20 runs or 14 days.

## Final Excerpt

+            "sfpcl_credit.communications.modules.communication_dispatcher."
             "ManualEmailDeliveryAdapter",
             return_value=RejectingAdapter(),
         ):
@@ -531,6 +736,48 @@
         self.assertEqual(rejected.json()["error"]["code"], "DELIVERY_FAILED")
         self._assert_no_advice_truth()
 
+    def test_provider_rejection_and_malformed_results_leave_outbox_retryable(self):
+        class RejectingAdapter:
+            def send_email(self, payload, idempotency_key):
+                raise ValueError("provider rejected")
+
+        class MalformedAdapter:
+            def send_email(self, payload, idempotency_key):
+                return {"delivery_status": "sent"}
+
+        for adapter in (RejectingAdapter(), MalformedAdapter()):
+            with self.subTest(adapter=adapter.__class__.__name__):
+                with patch(
+                    "sfpcl_credit.communications.modules.communication_dispatcher."
+                    "ManualEmailDeliveryAdapter",
+                    return_value=adapter,
+                ):
+                    response = self._post()
+                self.assertEqual(response.status_code, 409, response.content)
+                self.assertEqual(response.json()["error"]["code"], "DELIVERY_FAILED")
+                outbox = CommunicationDeliveryOutbox.objects.get(
+                    advice_intent=self.row.advice_intent
+                )
+                self.assertEqual(outbox.delivery_status, "pending")
+                self.assertIsNone(outbox.provider_external_message_id)
+                self.assertFalse(
+                    DisbursementAdviceDeliveryReceipt.objects.filter(
+                        advice_intent=self.row.advice_intent
+                    ).exists()
+                )
+                self._assert_no_advice_truth()
+
+        accepted = self._post()
+        self.assertEqual(accepted.status_code, 200, accepted.content)
+        outbox.refresh_from_db()
+        self.assertEqual(outbox.delivery_status, "sent")
+        self.assertEqual(
+            outbox.provider_external_message_id,
+            DisbursementAdviceDeliveryReceipt.objects.get(
+                advice_intent=self.row.advice_intent
+            ).external_message_id,
+        )
+
     def test_permission_scope_and_stale_transfer_fail_closed(self):
         wrong_role = self.owner.owner.fixture.fixture._user(
             "field_officer", "Advice Scope Outsider"

tokens used
260,534
Slice `009H3BA-communications-dispatcher-outbox-freeze` is complete pending independent orchestrator validation.

Implemented:

- Communications-owned template resolution, validation, rendering, outbox freeze, adapter dispatch, and provider-result validation.
- Durable outbox commit before provider invocation.
- Crash-safe accepted-result recovery using one stable provider identity.
- Fail-closed recipient, template provenance, payload, entity, and retained provider-result reconciliation.
- Manual/Fake/Future rejection, malformed-result, retry, and replay contracts.
- One-way frozen context seam with no communications-to-disbursements executable dependency.
- No migration, model, frontend, dependency, financial-state, or public API shape changes.

Verification passed:

- 28 focused tests; 2 expected PostgreSQL-only tests deferred to 009H3BB.
- Django system check.
- Migration sync.
- Python compilation.
- Dependency, protected-path, whitespace, and diff checks.
- Candidate size: 1,148 non-run changed lines, within limits.

Required state, progress, handoff, digest, slice status, risk assessment, evidence, and review artifacts are updated. See [final-summary.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_081752_normal_run/.ralph/runs/2026-07-18_081752_normal_run/final-summary.md) and [review-packet.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_081752_normal_run/.ralph/runs/2026-07-18_081752_normal_run/review-packet.md).

No git add, commit, or push was run. Next slice: `009H3BB-communications-finalization-and-race-closure`.
