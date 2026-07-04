# Review Packet — 002EYA E2E Baseline Capture and Seed Safety

## Traceability
- Slice says Playwright baselines must exist for login, dashboard, tracer closed, missing-session login, invalid-login error, and zero-permission dashboard. The repo has six tracked PNGs under `sfpcl-lms/e2e/*-snapshots/`, verified with `git ls-files`.
- Slice says E2E backend commands must not fall back to bare Python. `sfpcl-lms/playwright.config.ts` now throws if `E2E_DJANGO_PYTHON` is unset and names the Ralph venv interpreter.
- Slice says deterministic E2E users must not seed outside explicit local/E2E mode. `seed_e2e_users` now requires `SFPCL_DEBUG=true` and `SFPCL_ALLOW_E2E_SEED=true`; backend tests prove refusal without the guard and success with the guard.
- Slice says deterministic users must stay limited to the isolated Playwright sqlite DB. Playwright passes the seed flag only in the backend web-server env that also sets `SFPCL_DB_PATH`.

## Evidence
- Red seed guard: `.ralph/runs/2026-07-04_125854_normal_run/evidence/terminal-logs/seed-guard-red.log`
- Green seed guard: `.ralph/runs/2026-07-04_125854_normal_run/evidence/terminal-logs/seed-guard-green.log`
- Missing interpreter fail-fast: `.ralph/runs/2026-07-04_125854_normal_run/evidence/terminal-logs/e2e-missing-python-fail-fast.log`
- E2E with interpreter blocked by sandbox web-server startup: `.ralph/runs/2026-07-04_125854_normal_run/evidence/terminal-logs/e2e-green-or-blocked.log`
- Backend check: `.ralph/runs/2026-07-04_125854_normal_run/evidence/terminal-logs/backend-check.log`
- Backend tests: `.ralph/runs/2026-07-04_125854_normal_run/evidence/terminal-logs/backend-tests.log`
- Backend migrations check: `.ralph/runs/2026-07-04_125854_normal_run/evidence/terminal-logs/backend-migrations-check.log`
- Backend coverage: `.ralph/runs/2026-07-04_125854_normal_run/evidence/terminal-logs/backend-coverage.log`
- Frontend typecheck/lint/tests/build: `.ralph/runs/2026-07-04_125854_normal_run/evidence/terminal-logs/frontend-typecheck.log`, `frontend-lint.log`, `frontend-tests.log`, `frontend-build.log`

## Gate Results
- Backend `manage.py check`: passed.
- Backend tests: 65 passed.
- Backend migrations check: passed, no changes detected.
- Backend coverage: 96%, floor 85%.
- Frontend typecheck: passed.
- Frontend lint: passed.
- Frontend unit tests: 23 passed.
- Frontend build: passed.
- E2E: fail-fast behavior passed; full browser/web-server run blocked locally by sandbox `EPERM`.

## Notes for Reviewer
No production UI styling changed. No schema changes were made. No protected files were modified.
