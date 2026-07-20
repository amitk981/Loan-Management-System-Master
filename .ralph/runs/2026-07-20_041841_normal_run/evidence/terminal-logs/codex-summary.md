# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 12983620
Lines: 287048
SHA-256: 7ddd6d9278fd18281e1017862f9b6be8d89c3e5941b345ccd17a877e1fb952b2
Session ID: 019f7c91-7f05-7853-8db1-7cfac7eb2680
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+            ContentTemplate.objects.create(
+                template_code=code,
+                template_name=f"PG rate {channel}",
+                template_type=channel,
+                audience="borrower",
+                subject_template=subject,
+                body_template="Rate {{effective_rate}} from {{effective_from}}.",
+                variables_json=["effective_rate", "effective_from"],
+                approval_status="approved",
+                template_version="1.0",
+                effective_from=timezone.localdate(),
+            )
+        row = self._proposal(version="PG-RATE-NOTICE", effective_from="2026-08-01")
+        row.communication_required = True
+        row.save(update_fields=["communication_required"])
+        outcomes = self._race(
+            (row.pk, "pg-notice-a"),
+            (row.pk, "pg-notice-b"),
+        )
+        self.assertEqual(sorted(outcomes), ["conflict", "success"])
+        self.assertEqual(
+            BorrowerRateNoticeObligation.objects.filter(
+                interest_rate_config=row, loan_account=account
+            ).count(),
+            1,
+        )
+
+    def _race(self, *requests):
+        barrier = Barrier(len(requests))
+        checker_id = self.checker.pk
+
+        def contender(item):
+            close_old_connections()
+            try:
+                checker = User.objects.get(pk=checker_id)
+                barrier.wait(timeout=15)
+                try:
+                    activate(
+                        actor=checker,
+                        request=self.request,
+                        interest_rate_config_id=item[0],
+                        idempotency_key=item[1],
+                    )
+                    return "success"
+                except InterestRateConflict:
+                    return "conflict"
+            finally:
+                connections["default"].close()
+
+        with ThreadPoolExecutor(max_workers=len(requests)) as pool:
+            return list(pool.map(contender, requests))

tokens used
358,101
Implemented slice `010E2-effective-rate-versioning-and-borrower-notices` and marked the review packet **Ready for independent validation**.

Delivered:

- Governed floating-rate proposals with effective dates and immutable history.
- Maker-checker activation with configuration and communication permissions.
- Contiguous period enforcement, overlap/gap rejection, and deterministic historical resolution.
- Immutable invoice/accrual rate-consumption snapshots.
- One loan-level borrower-notice obligation linked to email and SMS communications.
- Honest pending, retrying, failed, and provider-accepted delivery truth.
- Section 41.4 list/create/activate endpoints and API documentation.
- One non-destructive migration.
- TDD RED/GREEN evidence, boundary matrix, contract examples, risk assessment, and review packet.
- Assumption A-145 documenting unresolved benchmark/reset/penal-interest policy.

Validation completed:

- Final focused gate: 51 tests passed under SQLite; three PostgreSQL-only tests skipped there.
- PostgreSQL acceptance executed twice: 3/3 tests passed on both runs with zero skips.
- Existing configuration and communications regressions passed.
- `manage.py check` passed.
- `makemigrations --check` reported no changes.
- `git diff --check` passed.
- No frontend, protected, source, state, progress, slice-status, or handoff files were modified.

The complete backend coverage suite remains reserved for Ralph’s independent validator, as required. No commit, add, or push commands were run.
