# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 10792259
Lines: 214546
SHA-256: 05570edc7a3c92caea69ea08b98f8b416599223caf230ae344e0e1917ca3608d
Session ID: 019f849c-4cda-7833-9d4c-0f8c3d08c9ba
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+            updated_by="Compliance User",
+            quick_actions=[],
+        )
+        global_search.register_compliance_provider(
+            lambda **_kwargs: [card]
+        )
+        try:
+            response = self._search("Searchable Farmer")
+            self.assertEqual(response.status_code, 200, response.content)
+            projected = response.json()["data"]["groups"]["compliance_records"]["items"][0]
+            self.assertEqual(set(projected), set(card))
+            self.assertEqual(projected["title"], "Section 186 review")
+        finally:
+            global_search.register_compliance_provider(lambda **_kwargs: [])
+
+    def test_rejects_unauthenticated_unknown_short_wildcard_and_malformed_requests(self):
+        unauthenticated = self.client.post(
+            self.URL,
+            data={"search": "Farmer"},
+            content_type="application/json",
+        )
+        self.assertEqual(unauthenticated.status_code, 401)
+        assert_error_envelope(self, unauthenticated.json(), "AUTH_REQUIRED")
+
+        for body in (
+            {"search": "x"},
+            {"search": "%Farmer"},
+            {"search": "Farmer", "unknown": True},
+            {"search": ["Farmer"]},
+        ):
+            with self.subTest(body=body):
+                response = self.client.post(
+                    self.URL,
+                    data=json.dumps(body),
+                    content_type="application/json",
+                    headers=self._headers(),
+                )
+                self.assertEqual(response.status_code, 400, response.content)
+                assert_error_envelope(self, response.json(), "VALIDATION_ERROR")
+
+    def test_rate_limit_uses_actor_identity_and_returns_safe_error(self):
+        for _ in range(30):
+            self.assertEqual(self._search("Searchable Farmer").status_code, 200)
+        limited = self._search("Searchable Farmer")
+        self.assertEqual(limited.status_code, 429, limited.content)
+        assert_error_envelope(self, limited.json(), "RATE_LIMITED")
+        self.assertNotIn("Searchable Farmer", limited.content.decode())

tokens used
362,645
Implemented slice `010N-global-search-api-and-ui` and marked it ready for independent validation.

Delivered:

- Privacy-safe `POST /api/v1/global-search/` with seven permission-filtered group seams, independent pagination, deterministic caps, validation, and rate limiting.
- Six currently available result groups plus the default-empty compliance provider for 011M3.
- Keyed-hash PAN, Aadhaar, and cheque matching; indexed Aadhaar/bank suffix and share-count searches.
- One non-destructive migration with Aadhaar suffix backfill.
- API-backed Global Search UI with loading, empty, partial, error, unauthorised, success, and per-group pagination states.
- Removed Header’s client-side mock/sensitive search index.
- Added the exact `e2e/global-search.e2e.spec.ts` contract for both required screenshots.

Validation completed:

- 27 focused backend and reverse-consumer tests passed.
- 5 focused frontend tests passed.
- Django check and migration-sync check passed.
- Typecheck, ESLint, and production build passed.
- Indexed query plans confirmed for all measured sensitive/suffix paths.
- Playwright collected the declared browser test successfully.
- No protected files, source documents, dependencies, Git metadata, or unrelated slices were changed.

Ralph’s independent gate still owns the complete backend coverage run and two real-browser executions producing `global-search-results.png` and `global-search-empty.png`; no screenshots were fabricated in the sandbox.

Artifacts:

- [Review packet](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_174720_normal_run/.ralph/runs/2026-07-21_174720_normal_run/review-packet.md)
- [Risk assessment](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_174720_normal_run/.ralph/runs/2026-07-21_174720_normal_run/risk-assessment.md)
- [Final summary](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_174720_normal_run/.ralph/runs/2026-07-21_174720_normal_run/final-summary.md)
- [Execution plan](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-21_174720_normal_run/.ralph/runs/2026-07-21_174720_normal_run/execution-plan.md)
