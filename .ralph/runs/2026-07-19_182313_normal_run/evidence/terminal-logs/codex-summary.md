# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 11991489
Lines: 252483
SHA-256: c4ee7cba0faea963a54589ab1185e829e91274194a25c7d24ae388582107bde9
Session ID: 019f7a70-8cae-7322-bfb8-1fa27a07cdb8
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+        ).get(
+            loan_application_id=fixture.account.loan_application_id,
+            request_status=SapCustomerProfileRequest.STATUS_COMPLETED,
+        )
+        request.sent_communication.body_snapshot = "PostgreSQL send-owner drift."
+        request.sent_communication.save(update_fields=["body_snapshot"])
+
+        response = Client().get("/api/v1/loan-accounts/", **fixture.auth)
+
+        self.assertEqual(response.status_code, 200, response.content)
+        self.assertEqual(response.json()["pagination"]["total_count"], 0)
+        self.assertEqual(response.json()["data"], [])
+
+    def test_s37_file_digest_owner_is_excluded_before_count(self):
+        fixture = workspace_tests.SapStaffWorkspaceApiTests(
+            "test_exact_assignee_gets_optional_s37_completion_action"
+        )
+        fixture.setUp()
+        request_id = fixture.fixture._create_and_send("postgresql-s37-file-drift")
+        request = SapCustomerProfileRequest.objects.select_related("excel_file").get(
+            pk=request_id
+        )
+        request.excel_file.checksum_sha256 = "0" * 64
+        request.excel_file.save(update_fields=["checksum_sha256"])
+
+        response = Client().get(
+            "/api/v1/disbursement-workspaces/",
+            **fixture.fixture._auth(fixture.fixture.assignee),
+        )
+
+        self.assertEqual(response.status_code, 200, response.content)
+        self.assertEqual(response.json()["pagination"]["total_count"], 0)
+        self.assertEqual(response.json()["data"], [])
diff --git a/sfpcl_credit/tests/test_sap_model_ownership_migration.py b/sfpcl_credit/tests/test_sap_model_ownership_migration.py
index f3c27a9bd0899ea29efb57705c274ed38d859c4e..44effcea0e86f30cf467d929a790f55eb493a6fa
--- a/sfpcl_credit/tests/test_sap_model_ownership_migration.py
+++ b/sfpcl_credit/tests/test_sap_model_ownership_migration.py
@@ -113,8 +113,12 @@
     def test_forward_and_reverse_transfer_preserve_exact_business_state(self):
         self.executor = MigrationExecutor(connection)
         self.executor.migrate(self.migrate_to)
+        moved_targets = [
+            node for node in self.executor.loader.graph.leaf_nodes()
+            if node[0] != "sap_workflow"
+        ] + self.migrate_to
         moved_apps = self.executor.loader.project_state(
-            self.executor.loader.graph.leaf_nodes()
+            moved_targets
         ).apps
 
         with self.assertRaises(LookupError):

tokens used
461,480
Implemented slice `009L7-epic-009-read-boundary-convergence-closure` and prepared it for Ralph’s independent validation.

Key results:

- Restored strict public Loan Account read permission and object scope.
- Added a separate staff initiation-candidate boundary.
- Removed post-pagination Loan Account projection drops.
- Expanded SAP send/completion integrity selection, including immutable Annexure-I storage checksums.
- Strengthened CFC/account/bank eligibility before pagination.
- Added targeted and full-suite Playwright fixture-family selection.
- Added permanent convergence and six-test PostgreSQL acceptance coverage.
- Completed `execution-plan.md`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.
- Set the review result exactly to `Ready for independent validation`.

Validation evidence:

- Final owner-boundary tests: 35 passed.
- Focused backend tests: 83 passed, 9 PostgreSQL-only skips.
- Reverse-consumer tests: 39 passed.
- PostgreSQL acceptance: 6 tests passed twice without skips.
- Frontend: 355 tests passed; typecheck, lint, and build passed.
- Backend system and migration checks passed.
- Full Playwright collection: 35 tests across 20 files.
- Targeted Epic 009 Playwright spec collected successfully.

The local Chromium run was blocked by the expected macOS sandbox restriction. No screenshots were fabricated; Ralph’s external browser gate remains authoritative for the two runs and nine screenshot hashes. No protected files, source documents, Ralph mechanical state files, or git metadata were modified.
