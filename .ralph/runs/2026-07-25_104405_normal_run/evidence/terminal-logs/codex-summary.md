# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 11642944
Lines: 249686
SHA-256: 5accdc382c2e3e138cf049c170f2c91e977f830f2c5941441f2336b80339920f
Session ID: 019f97b2-44c4-7ee2-943b-7d95f23d8791
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+        user.save()
+        for permission_code in sorted(REQUIRED_SMOKE_PERMISSIONS):
+            permission, _created = Permission.objects.get_or_create(
+                permission_code=permission_code,
+                defaults={
+                    "permission_name": permission_code,
+                    "module_name": permission_code.split(".", 1)[0],
+                    "risk_level": Permission.RISK_MEDIUM,
+                },
+            )
+            RolePermission.objects.create(role=role, permission=permission)
+
+    def test_smoke_check_against_local_server_does_not_write_business_records(
+        self,
+    ):
+        business_counts_before = self._business_counts()
+        stdout = StringIO()
+
+        with patch.dict(
+            os.environ,
+            {
+                "SFPCL_SMOKE_CHECK_EMAIL": "smoke.reader@sfpcl.example",
+                "SFPCL_SMOKE_CHECK_PASSWORD": "SyntheticPassword123!",
+            },
+        ):
+            call_command(
+                "smoke_check",
+                base_url=self.live_server_url,
+                stdout=stdout,
+            )
+
+        self.assertEqual(self._business_counts(), business_counts_before)
+        self.assertIn(
+            "Smoke check passed: 8 read-only workflows",
+            stdout.getvalue(),
+        )
+
+    @staticmethod
+    def _business_counts():
+        return {
+            "members": Member.objects.count(),
+            "applications": LoanApplication.objects.count(),
+            "approval_cases": ApprovalCase.objects.count(),
+            "loan_accounts": LoanAccount.objects.count(),
+        }

tokens used
498,139
Slice `012H-deployment-readiness-and-smoke-checks` is ready for independent validation.

Delivered:

- Public, zero-database-query `GET /health/live/`.
- Public `GET /health/ready/` covering database connectivity, migration state, and critical signing/encryption configuration.
- Sanitized, machine-readable readiness failures.
- Read-only `manage.py smoke_check --base-url` with:
  - environment-only credentials;
  - exact dedicated `deployment_smoke_reader` identity and permission validation;
  - admin rejection;
  - eight bounded workflow reads spanning all four 012G module groups;
  - legible stage-specific failures.
- Dedicated local E2E smoke user and exact two-repetition Playwright contract.
- API contract, assumption, performance, risk, and review evidence.

Validation completed:

- 22 focused backend tests passed.
- Final smoke-command tests passed.
- Isolated deployed-process smoke passed all eight workflows in 0.87 seconds.
- Django system and migration checks passed.
- Impacted frontend tests: 9 passed.
- Frontend typecheck, lint, and production build passed.
- Playwright discovered both required contract repetitions.
- `git diff --check`, protected-path audit, and evidence-path audit passed.

Chrome exited during both bounded local browser attempts before a page was created. No screenshot was fabricated; trusted validation must produce `deployment-smoke-readiness.png`.

Review handoff: [review-packet.md](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-25_104405_normal_run/.ralph/runs/2026-07-25_104405_normal_run/review-packet.md)

No git add, commit, merge, or push was performed.
