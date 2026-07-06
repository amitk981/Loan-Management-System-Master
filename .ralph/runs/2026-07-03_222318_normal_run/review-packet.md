# Review Packet — 002E Protected Frontend Route Shell

## Summary
Implemented the backend-backed staff frontend auth shell:
- `LoginScreen` now submits email/password to the parent staff auth flow.
- `App` restores stored staff sessions, logs in through `/api/v1/auth/login/`, loads `/api/v1/auth/me/`, clears invalid sessions, and logs out through `/api/v1/auth/logout/`.
- `RoleContext` derives current user display, role/team compatibility codes, canonical permissions, and `can(...)` checks from backend `/auth/me/` payloads.
- `Header` hides the demo role switcher unless `VITE_ENABLE_DEMO_AUTH === "true"` and displays backend role/team names.
- Existing borrower portal demo auth remains unchanged.

## Traceability
- Source/digest says 002E must use backend login → `/auth/me/` before rendering staff navigation and must preserve borrower demo auth. Code does this in `sfpcl-lms/src/App.tsx` and `sfpcl-lms/src/services/authSession.ts`; tested by `sfpcl-lms/src/services/authSession.test.ts`.
- Source/digest says `/auth/me/` `roles`/`teams` objects are the display source and compatibility code arrays must match those objects. Code derives `roleCodes`/`teamCodes` from `roles`/`teams` in `mapBackendUserToFrontendUser`; tests assert object-derived display and compatibility values.
- Source/digest says canonical backend permissions are source of truth and unknown mappings must not invent grants. Code maps canonical codes in `mapCanonicalPermissions`, drops unmapped codes, and records A-010 in `docs/working/ASSUMPTIONS.md`; tests assert unknown codes grant no prototype permission.
- Slice says invalid credentials and expired/invalid sessions return to login without exposing protected content. Service tests cover invalid login and `TOKEN_EXPIRED` clearing stored auth; App maps these errors to existing login error styles.
- Slice says logout calls backend with refresh token and returns to login. Service test covers `/auth/logout/` request body and local auth clearing.

## Validation
- Frontend TDD red failed on missing `authSession` module as expected.
- Frontend targeted green: 7 auth/session tests passed.
- Frontend full suite: 12 tests passed.
- Frontend typecheck passed.
- Frontend build passed.
- Backend check passed.
- Backend tests passed: 52 tests.
- Backend migrations check passed: no changes detected.
- Backend coverage passed: 97%, above 85% floor.
- API/CORS smoke via Django test client passed for health, login, `/auth/me/`, logout, and revoked-session `/auth/me/`.

## Visual Evidence
Generated local built-bundle harness pages for login, loading session, authenticated dashboard, invalid login, and limited-permission dashboard under `evidence/visual-harness/`. Actual screenshot capture was blocked by sandbox/runtime constraints: Django/Vite could not bind listening sockets (`EPERM`) and Chrome headless exited 134 before writing images. This is recorded in `screenshot-results.md`.

## Follow-Up
002EX and 002EY were sharpened to consume the real 002E auth path and to avoid demo-auth bypasses in tracer/E2E evidence.
