# Risk Assessment — 002E Protected Frontend Route Shell

## Risk Level
Medium.

## Why
- The slice changes staff authentication/session flow and frontend route/sidebar authorization.
- It consumes existing backend auth endpoints but does not alter backend auth behavior, database schema, migrations, or financial/business rules.

## Controls
- Backend remains authoritative for authentication and permissions.
- Staff shell renders only after backend login and `/api/v1/auth/me/` success.
- Token restore failures for `TOKEN_EXPIRED` and `INVALID_TOKEN` clear local state and return to login.
- Demo staff role switching is disabled by default and only available with `VITE_ENABLE_DEMO_AUTH === "true"`.
- Permission bridge maps only known canonical backend permission codes to existing prototype permission names; unmapped codes grant no UI access and are recorded in A-010.

## Evidence
- Frontend TDD red: `evidence/terminal-logs/frontend-auth-session-red.log`
- Frontend TDD green: `evidence/terminal-logs/frontend-auth-session-green.log`
- Frontend final tests/typecheck/build: `test-results.md`, `typecheck-results.md`, `build-results.md`
- Backend gates: `backend-check-results.md`, `backend-test-results.md`, `backend-migrations-results.md`, `backend-coverage-results.md`
- API/CORS smoke: `evidence/terminal-logs/api-cors-smoke.log`

## Caveats
- Localhost dev servers could not bind in this sandbox (`EPERM`), so live browser/API smoke through `127.0.0.1:8000` and `localhost:5173` was not possible.
- Chrome headless exited 134 before writing screenshots. Visual harness files are saved in `evidence/visual-harness/`, and the limitation is recorded in `screenshot-results.md`.
