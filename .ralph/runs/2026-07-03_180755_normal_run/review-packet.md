# Review Packet: 2026-07-03_180755_normal_run

## Result
Complete with local dependency-install caveat

## Slice
002D2-backend-dev-infrastructure

## What Changed
- `sfpcl_credit/config/settings.py` now reads safe dev settings from environment variables and uses `sfpcl_credit/db.sqlite3` for development.
- `django-cors-headers==4.4.0` is pinned and CORS is configured for `http://localhost:5173`.
- Backend tests now rely on Django's migrated `TestCase` database through `sfpcl_credit/tests/base.py`; duplicated manual table creation was removed.
- Added infrastructure tests for settings parsing, CORS behavior, and manual-schema guardrail.
- Added a Dev Setup section to `docs/working/API_CONTRACTS.md`.
- Sharpened `002E` and `002EX` with 002D2 dependency details and updated the Epic 002 digest.

## Traceability
- Slice says settings must read `SFPCL_SECRET_KEY`, `SFPCL_DEBUG`, `SFPCL_ALLOWED_HOSTS`, and `SFPCL_CORS_ORIGINS`; code does this in `settings.py`; verified statically by `settings-env-static.log` and by new tests in `test_backend_infrastructure.py`.
- Slice says dev database must be persistent SQLite; code sets the default DB name to `BASE_DIR / "db.sqlite3"`; verified statically in `settings-env-static.log`.
- Slice says CORS must allow `http://localhost:5173`; code pins and configures `django-cors-headers`; runtime verification is blocked locally until dependency installation.
- Slice says backend tests must stop manually creating identity tables; target test modules now use `TestCase`/`IdentityTestCase`; verified by `schema-setup-grep-after-cleanup.log`.
- Slice says `/auth/me/` contract must stay stable; the existing auth tests were preserved and moved onto migrated database setup. Runtime re-verification is blocked locally by the missing newly pinned package.

## Evidence Summary
- RED: `evidence/terminal-logs/red-backend-infrastructure-tests.log`
- Backend static green: `backend-compileall-after-cleanup.log`, `settings-env-static.log`, `schema-setup-grep-after-cleanup.log`
- Backend dependency-blocked gates: `backend-check.log`, `backend-tests.log`, `backend-makemigrations-check.log`, `backend-migrate-dev-db.log`, `backend-coverage.log`
- Frontend green: `frontend-typecheck.log`, `frontend-test.log`, `frontend-build.log`

## Recommended Next Action
Install pinned backend requirements through the orchestrator, then rerun backend check/tests/migrations/coverage and the dev DB auth smoke. Continue to `002E-protected-frontend-route-shell` after validation.
