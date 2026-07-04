# Review Packet: 2026-07-04_184602_normal_run

## Result
Success

## Slice
002K-seed-data-and-demo-users

## Summary
Added `seed_demo_users`, a guarded local/dev management command that creates deterministic
demo staff users only when `SFPCL_DEBUG=true` and `SFPCL_ALLOW_DEMO_SEED=true`. It calls the
canonical catalogue seed, binds demo users to existing active roles/teams, keeps E2E users
separate, updates known demo users idempotently, and does not add schema/frontend/auth-bypass
behavior.

## Traceability
- Source/digest says predictable seed users must follow the 002EYA guard pattern:
  command refuses without `SFPCL_DEBUG=true` plus explicit demo flag; verified by
  `test_seed_refuses_without_explicit_demo_guard` and
  `test_seed_refuses_when_debug_is_true_but_demo_flag_is_missing`.
- Source/digest says demo users must use real auth: tests login through
  `/api/v1/auth/login/` and call `/api/v1/auth/me/`; examples saved in
  `api-response-examples.md`.
- Source/digest says no broad permission aliases: tests assert system admin has canonical
  `users.user.*` permissions but no `manage_users`, tracer-only has exactly
  `tracer.lifecycle.run`, and zero-permission has empty `permissions`/`available_actions`.
- Source/digest says use 002J harness: tests use `assert_success_envelope`,
  `assert_error_envelope`, and `assert_pagination_shape` for `/auth/me`, admin list, and
  permission-denied responses.
- Audit expectation says login/logout retain existing auth audit path: verified by
  `test_login_and_logout_use_existing_auth_audit_path`.

## Evidence
- RED: `evidence/terminal-logs/seed-demo-red-001.log`,
  `evidence/terminal-logs/seed-demo-red-002.log`
- GREEN: `evidence/terminal-logs/seed-demo-green-001.log`,
  `evidence/terminal-logs/seed-demo-green-003.log`,
  `evidence/terminal-logs/seed-demo-green-004.log`
- Backend gates: `backend-check.log`, `backend-tests.log`,
  `backend-makemigrations-check.log`, `backend-coverage-report.log`
- Frontend gates: `frontend-typecheck.log`, `frontend-lint.log`,
  `frontend-tests.log`, `frontend-build.log`
- API examples: `api-response-examples.md`
- Changed files: `changed-files.txt`

## Gate Results
- Backend check: pass.
- Backend tests: 107/107 pass.
- Backend migrations: no changes detected.
- Backend coverage: 96%, floor 85%.
- Frontend typecheck: pass.
- Frontend lint: pass.
- Frontend tests: 26/26 pass.
- Frontend build: pass.

## Recommended Next Action
Run architecture review next by cadence, then continue with `003A-audit-log-foundation`.
