# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 2354477
Lines: 44173
SHA-256: 757d54ed2d49192e5b0b3cbfc12ca66012213bb9758eb131f499e857de9894be
Session ID: 019f7375-be31-7633-8ee2-8527a4974803
Raw retention: operator-local, at most 20 runs or 14 days.

## Final Excerpt

+                }
             }
+            for name, details in physical.items()
+        }
+        return {
+            "checklist": {key: str(value) for key, value in checklist.items()},
+            "action": {key: str(value) for key, value in action.items()},
+            "live_physical_constraint_counts": {
+                name: int(name in physical) for name in self.live_constraints
+            },
+            "retired_physical_constraint_counts": {
+                name: int(name in physical) for name in self.retired_constraints
+            },
+            "physical_schema": physical_schema,
+        }
+
+    def _assert_live_constraint_manifest(self, apps, manifest):
+        DocumentChecklist = apps.get_model("legal_documents", "DocumentChecklist")
+        state_names = [
+            constraint.name for constraint in DocumentChecklist._meta.constraints
+        ]
+        for name in self.live_constraints:
+            self.assertEqual(state_names.count(name), 1, state_names)
+            self.assertEqual(manifest["live_physical_constraint_counts"][name], 1)
+        for name in self.retired_constraints:
+            self.assertEqual(state_names.count(name), 0, state_names)
+            self.assertEqual(manifest["retired_physical_constraint_counts"][name], 0)
+
+
+class LegalChecklistMigrationOwnershipGuardTests(SimpleTestCase):
+    def test_guard_rejects_synthetic_cross_app_checklist_state_mutation(self):
+        synthetic = {
+            Path("future_app/migrations/0001_bad.py"): """
+from django.db.migrations.operations.base import Operation
+
+class BadChecklistMutation(Operation):
+    def state_forwards(self, app_label, state):
+        state.models[("legal_documents", "documentchecklist")].options.clear()
+"""
+        }
+
+        self.assertEqual(
+            legal_checklist_state_ownership_violations(sources=synthetic),
+            ["future_app/migrations/0001_bad.py:BadChecklistMutation"],
+        )
+
+    def test_guard_allows_only_reviewed_009g2_history_in_repository(self):
+        package_root = Path(__file__).resolve().parents[1]
+        self.assertEqual(
+            LEGAL_CHECKLIST_STATE_ALLOWLIST,
+            {
+                "disbursements/migrations/"
+                "0005_disbursementadviceintent_loanregisterupdate_and_more.py:"
+                "AddLegalChecklistConstraint",
+                "disbursements/migrations/"
+                "0005_disbursementadviceintent_loanregisterupdate_and_more.py:"
+                "RemoveLegalChecklistConstraint",
+            },
+        )
+        self.assertEqual(
+            legal_checklist_state_ownership_violations(package_root=package_root),
+            [],
+        )

tokens used
207,318
Completed Ralph slice `009G4-legal-checklist-migration-ownership-anchor`.

- Added a zero-SQL `legal_documents` migration anchoring the historical checklist constraint state and current G3/H3B leaves.
- Added an executable static guard preventing future downstream custom migrations from changing legal checklist model state.
- Preserved checklist/action IDs, rows, constraint names, and complete physical schema through forward, reverse, and reapply.
- Saved failing-first and green TDD evidence.
- Passed 6 focused tests and 7 adjacent migration-isolation tests.
- Passed Django check, migration sync, compilation, and zero-operation SQL verification.
- Passed Node 20 typecheck, lint, all 327 frontend tests, and production build.
- Updated the slice, Epic 009 digest, state, progress, handoff, risk assessment, review packet, final summary, and changed-files manifest.
- Rechecked 009I and 009J; both are already concretely sharpened.
- Protected paths remain untouched; queue lint, changed-file reconciliation, and whitespace checks pass.

The independent orchestrator backend coverage gate and commit/merge remain pending, as required. No `git add`, commit, or push was run.
