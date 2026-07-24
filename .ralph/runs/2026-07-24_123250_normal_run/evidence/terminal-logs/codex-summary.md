# Agent Log Summary

Agent: codex
Exit code: 0
Bytes: 8158153
Lines: 150879
SHA-256: 0a6ea0eea83e77518dd81839894664cf5d3c2d186073eb13f44bdf25cec8fe9c
Session ID: 019f92ef-70bd-78c2-903f-d5862a78a53b
Raw retention: operator-local, at most 20 runs, 14 days, or 67108864 bytes (the active run is always preserved).

## Final Excerpt

+            "/api/v1/portal/auth/login/",
+            data={
+                "identifier": user.email,
+                "password": "E2eTracer123!",
+            },
+            content_type="application/json",
+        )
+
+        self.assertEqual(response.status_code, 401, response.content)
+        self.assertFalse(UserSession.objects.filter(user=user).exists())
+
+    def test_production_settings_refuse_all_demo_seed_commands(self):
+        probe = """
+import django
+django.setup()
+
+from django.conf import settings
+from django.core.management import call_command
+from django.core.management.base import CommandError
+
+assert settings.ENABLE_DEMO_SURFACES is False
+for command_name in (
+    "seed_demo_users",
+    "seed_e2e_users",
+    "seed_portal_e2e_fixture",
+    "seed_epic_009_e2e_fixture",
+    "seed_approval_configuration",
+):
+    try:
+        call_command(command_name)
+    except CommandError as error:
+        assert "disabled by deployment settings" in str(error), str(error)
+    else:
+        raise AssertionError(f"{command_name} ran under production settings")
+"""
+        environment = {
+            **os.environ,
+            "DJANGO_SETTINGS_MODULE": "sfpcl_credit.config.production_settings",
+            "SFPCL_DEBUG": "true",
+            "SFPCL_ALLOW_DEMO_SEED": "true",
+            "SFPCL_ALLOW_E2E_SEED": "true",
+        }
+
+        result = subprocess.run(
+            [BACKEND_PYTHON, "-c", probe],
+            cwd=BACKEND_ROOT.parent,
+            env=environment,
+            capture_output=True,
+            text=True,
+            check=False,
+        )
+
+        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

tokens used
325,719
Implemented slice `012E2-tracer-and-demo-route-production-isolation` and prepared it for Ralph’s independent validation.

Key outcomes:

- Production Django does not install the tracer app or register/import tracer routes.
- All demo and E2E seed commands refuse to run under production settings.
- Existing synthetic `@sfpcl.example` staff and portal identities cannot authenticate or retain sessions in production.
- Production frontend builds omit tracer screens/APIs, demo identities, demo login controls, role switching, and the Agentation development endpoint.
- Tracer navigation is absent and direct navigation fails closed in production.
- Development tracer and guarded seed workflows remain operational.
- A-011 and API contract documentation were updated.

Validation completed:

- Backend impacted tests: 61 passed.
- Frontend tests: 437 passed.
- Frontend typecheck, lint, and production build passed.
- Normal and production Django checks passed.
- Migration synchronization passed.
- Production bundle static-exclusion proof passed.
- Protected paths remained untouched.
- No commit, push, state update, or slice status transition was performed.

The [review packet](/Users/amitkallapa/LMS/.ralph/worktrees/2026-07-24_123250_normal_run/.ralph/runs/2026-07-24_123250_normal_run/review-packet.md) result is exactly `Ready for independent validation`.
