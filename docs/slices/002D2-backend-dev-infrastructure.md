# Slice 002D2: Backend Dev Infrastructure — Env Settings, Persistent DB, CORS, Test Base

## Status
Not Started

## Parent Epic
Epic 002: Platform Auth and Role Shell (infrastructure)
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Remove the infrastructure landmines that would block frontend-backend stitching in 002E/002EX: in-memory development database, hardcoded settings, missing CORS, and duplicated backend test schema setup.

## User Value
The React app can actually talk to the backend in development, data survives between requests, and secrets are no longer written in source code.

## Depends On
- 002D

## Concrete Requirements
1. `sfpcl_credit/config/settings.py` reads from environment with safe dev fallbacks: `SFPCL_SECRET_KEY` (fallback stays dev-only), `SFPCL_DEBUG` (default true in dev), `SFPCL_ALLOWED_HOSTS` (comma-separated, default localhost).
2. Database: dev uses a persistent SQLite file `sfpcl_credit/db.sqlite3` (already gitignored). Tests keep using Django's automatic in-memory test database — verify test runtime stays fast.
3. Add `django-cors-headers` (pinned, in requirements.txt): allow origin `http://localhost:5173` (env-overridable via `SFPCL_CORS_ORIGINS`). Add Django's standard `CommonMiddleware` and `SecurityMiddleware` to the currently empty `MIDDLEWARE`.
4. `python3 sfpcl_credit/manage.py migrate` works against the dev database. Add a short "Dev Setup" note (migrate, runserver, npm run dev) at the top of `docs/working/API_CONTRACTS.md`.
5. Replace the repeated `django.setup()` / `schema_editor.create_model()` / manual table-clear helpers currently duplicated in backend test files with a shared Django test base or `TestCase`/fixture pattern that relies on migrations. The backend suite must no longer manually create identity tables in each test module.
6. No behaviour change to existing auth/health endpoints or their tests.

## Test Cases
- Existing auth + health tests pass unchanged.
- New test: response to a request with `Origin: http://localhost:5173` includes the CORS allow-origin header.
- New test: settings read `SFPCL_SECRET_KEY` from the environment when set.
- New test or static assertion: backend tests no longer contain duplicated `schema_editor.create_model` setup in `test_auth_api.py`, `test_auth_module.py`, `test_api_envelope.py`, or `test_catalogue_seed.py`.
- Existing catalogue/auth module tests still prove real behavior after the shared test base change: seed idempotency, refresh replay rejection, logout revocation, and shared response envelope.

## Out of Scope
PostgreSQL (arrives with deployment slices), production hardening, HTTPS, rate limiting.

## Risk Level
Medium

## Acceptance Criteria
- Frontend dev server can call `GET /api/v1/health/live/` cross-origin in development.
- Data persists across two consecutive API requests in dev.
- Backend tests rely on Django's migrated test database rather than per-file schema creation; `rg "schema_editor.create_model|ensure_.*tables" sfpcl_credit/tests` is empty or limited to a single shared test utility with a documented reason.
- All gates pass.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] Dependency pinned and recorded
- [ ] Tests/typecheck/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
