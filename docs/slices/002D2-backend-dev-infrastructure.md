# Slice 002D2: Backend Dev Infrastructure — Env Settings, Persistent DB, CORS, Test Base

## Status
Complete

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
7. Preserve the 002D `/api/v1/auth/me/` contract exactly while changing settings/test infrastructure: bearer access token, active session, active user, standard envelope with `meta.api_version`, `role_codes`, `team_codes`, sorted `permissions`, and `available_actions`.
8. Add a dev smoke note or test evidence showing a migrated persistent dev DB can support the auth flow across separate requests: create/seed a user, login, then call `/api/v1/auth/me/` with the returned access token.

## Test Cases
- Existing auth + health tests pass unchanged.
- New test: response to a request with `Origin: http://localhost:5173` includes the CORS allow-origin header.
- New test: settings read `SFPCL_SECRET_KEY` from the environment when set.
- New test: settings read `SFPCL_ALLOWED_HOSTS` and `SFPCL_CORS_ORIGINS` as comma-separated lists.
- New test or static assertion: backend tests no longer contain duplicated `schema_editor.create_model` setup in `test_auth_api.py`, `test_auth_module.py`, `test_api_envelope.py`, or `test_catalogue_seed.py`.
- Regression test: `/api/v1/auth/me/` still rejects a logged-out/revoked session with `401 INVALID_TOKEN` after the settings/test-base refactor.
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
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] Dependency pinned and recorded
- [ ] Tests/typecheck/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates

Note: frontend gates and backend static checks passed during `2026-07-03_180755_normal_run`; backend runtime gates were blocked locally because the newly pinned `django-cors-headers==4.4.0` package is not installed in the offline Ralph venv. Per the run prompt, the orchestrator installs pinned requirements before independent validation.
