# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 2621091
Lines: 53070
SHA-256: 04a95d84eb8f1529b7731664fbd543a59d717473c3189fa6e8eccd9f3e50c308
Session ID: 019f71b3-755d-7302-9007-87d46b8b9407
Raw retention: operator-local, at most 20 runs or 14 days.

## Final Excerpt

+        OldReceipt = old_apps.get_model(
+            "disbursements", "DisbursementAdviceDeliveryReceipt"
+        )
+        retained_id = str(OldReceipt.objects.get().pk)
+        before = self._receipt_signature()
+
+        moved_apps = self._migrate(self.migrate_to)
+        MovedReceipt = moved_apps.get_model(
+            "communications", "DisbursementAdviceDeliveryReceipt"
+        )
+        self.assertEqual(str(MovedReceipt.objects.get().pk), retained_id)
+        self.assertEqual(self._receipt_signature(), before)
+        self.assertEqual(self._outbox_table_count(), 1)
+
+        reversed_apps = self._migrate(self.migrate_from)
+        ReversedReceipt = reversed_apps.get_model(
+            "disbursements", "DisbursementAdviceDeliveryReceipt"
+        )
+        self.assertEqual(str(ReversedReceipt.objects.get().pk), retained_id)
+        self.assertEqual(self._receipt_signature(), before)
+        self.assertEqual(self._outbox_table_count(), 0)
+
+        reapplied_apps = self._migrate(self.migrate_to)
+        ReappliedReceipt = reapplied_apps.get_model(
+            "communications", "DisbursementAdviceDeliveryReceipt"
+        )
+        self.assertEqual(str(ReappliedReceipt.objects.get().pk), retained_id)
+        self.assertEqual(self._receipt_signature(), before)
+        self.assertEqual(self._outbox_table_count(), 1)
+
+    def _migrate(self, targets):
+        executor = MigrationExecutor(connection)
+        executor.migrate(targets)
+        return executor.loader.project_state(targets).apps
+
+    def _receipt_signature(self):
+        table = "disbursement_advice_delivery_receipts"
+        with connection.cursor() as cursor:
+            constraints = connection.introspection.get_constraints(cursor, table)
+            description = connection.introspection.get_table_description(
+                cursor, table
+            )
+        return {
+            "table": table,
+            "columns": tuple(field.name for field in description),
+            "constraints": tuple(sorted(constraints)),
+        }
+
+    def _outbox_table_count(self):
+        return connection.introspection.table_names().count(
+            "communication_delivery_outboxes"
+        )

tokens used
403,648
Slice `009H3A-communications-advice-persistence-and-provider-identity` is complete and ready for independent Ralph validation.

Implemented:

- Communications-owned durable advice outbox with frozen recipient, template, rendered payload, entity, idempotency, and provider-result facts.
- Reversible state-only ownership transfer of `DisbursementAdviceDeliveryReceipt`.
- Preserved physical receipt table, constraints, relations, historical rows, and primary keys across forward, reverse, and reapply.
- Stable-key provider identity across fresh Manual, Fake, and Future adapter instances.
- Retryable provider rejection without fabricated receipt, Communication, audit, workflow, or sent status.
- Policy-free legacy disbursements model alias with no communications-to-disbursements executable import.
- Existing 009H2 route, permissions, reconciliation, masking, audit, response, and financial behavior preserved.

Verification:

- 24 focused foundation and 009H2 tests passed.
- Two PostgreSQL-only race tests skipped as expected; 009H3B owns authoritative race closure.
- Django check and migration synchronization passed.
- Generated migration SQL, Python compilation, state JSON, whitespace, protected paths, and diff limits passed.
- 684 non-run changed lines across 12 files, one migration, and no new dependencies.
- No frontend, public API, dependency, permission, protected, or source-document changes.
- No git add, commit, merge, or push was performed.

Artifacts: [final-summary.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_013956_normal_run/.ralph/runs/2026-07-18_013956_normal_run/final-summary.md), [review-packet.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_013956_normal_run/.ralph/runs/2026-07-18_013956_normal_run/review-packet.md), and [evidence/README.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-18_013956_normal_run/.ralph/runs/2026-07-18_013956_normal_run/evidence/README.md).

Next queued work is the already-sharpened `009H3B` dispatcher, crash-window, and PostgreSQL race closure.
