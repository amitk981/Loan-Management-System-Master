# Execution Plan

Selected slice: 002D2-backend-dev-infrastructure

## Scope
- Backend-only infrastructure slice for `sfpcl_credit/`.
- Keep existing auth, health, and `/api/v1/auth/me/` behavior unchanged.
- No frontend code changes expected.
- Do not modify protected paths or `docs/source/`.

## Permissions Check
Allowed edit paths needed for this run:
- `sfpcl_credit/**`
- `docs/working/**`
- `docs/slices/**`
- `.ralph/runs/**`
- `.ralph/progress.md`
- `.ralph/state.json`

Protected/forbidden paths will not be edited:
- `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`
- `docs/working/HIGH_RISK_APPROVALS.md`, `docs/working/DECISION_POLICY.md`, `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/source/**`, `.git/**`, secrets/env files

## TDD Plan
1. Add backend tests for settings and CORS:
   - env-driven `SFPCL_SECRET_KEY`
   - comma-separated `SFPCL_ALLOWED_HOSTS`
   - comma-separated `SFPCL_CORS_ORIGINS`
   - `Origin: http://localhost:5173` receives `Access-Control-Allow-Origin`
   Save failing output in `evidence/terminal-logs/`.
2. Add/refactor tests to use Django's migrated test database:
   - replace per-file `django.setup()` / `schema_editor.create_model()` helpers with `django.test.TestCase`
   - add a static guardrail that the named backend tests no longer contain duplicated manual schema setup
   Save red/green evidence.
3. Implement minimal infrastructure changes:
   - settings env parsing helpers
   - persistent dev SQLite `sfpcl_credit/db.sqlite3`
   - add pinned `django-cors-headers`
   - enable `corsheaders`, `SecurityMiddleware`, `CommonMiddleware`, and CORS config
4. Update `docs/working/API_CONTRACTS.md` with a short Dev Setup note.
5. Run required gates/evidence:
   - backend `manage.py check`
   - backend tests
   - `makemigrations --check`
   - backend coverage
   - frontend typecheck/tests/build if available
   - `migrate` against dev SQLite and auth smoke evidence if dependency availability permits
6. Finish Ralph artifacts:
   - changed files
   - risk assessment
   - review packet
   - final summary
   - handoff/progress/state/slice status
   - sharpen next 1-2 Not Started slices using already-opened digest/epic context

## Known Dependency Constraint
`django-cors-headers` is pre-approved and required by the slice, but is not importable in the current Ralph venv before pinning/install. Network access is unavailable and `pip install` is forbidden. If local backend gates fail only because this newly pinned package is absent, record that in final summary and evidence; the orchestrator is expected to install pinned requirements before independent validation.
