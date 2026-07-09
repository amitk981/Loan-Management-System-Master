# Execution Plan: 005G2 Member Portal Session and Audit Contract Hardening

## Scope
- Add a shared portal-session validity boundary so inactive or suspended portal accounts cannot keep using already-issued portal sessions.
- Apply that boundary to `/api/v1/auth/me/`, portal password change, portal dashboard/profile/produce-supply reads, and portal application endpoints.
- Align borrower portal audit action names with `screen-spec-member-portal.md` while preserving existing staff `applications.loan_application.*` audit actions.
- Update `docs/working/API_CONTRACTS.md` with session invalidation and audit-name behavior.

## TDD Cycles
1. Add a focused failing backend test proving an old portal token stops exposing `/auth/me` portal claims after `PortalAccount.status = suspended` and revokes the session.
2. Implement the shared portal-session validity helper and wire current-user/session validation through it.
3. Add failing tests for old-token password-change and portal own-data/application endpoints after suspension.
4. Wire portal route helpers to the shared validity boundary and verify no success audit/application side effects.
5. Add failing tests for canonical portal audit action names and sensitive-payload exclusions.
6. Rename portal-only audit actions and pass a portal audit-action override into shared application services while keeping staff route audit names unchanged.

## Evidence
- Save red/green focused test output under `evidence/terminal-logs/`.
- Run backend checks, tests, migrations check, and coverage using `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Run frontend lint, typecheck, tests, and build because Ralph gates require them, even though no frontend change is expected.

## Files Expected
- Backend auth/portal service and view modules.
- Backend portal auth/member/application tests.
- `docs/working/API_CONTRACTS.md`.
- Ralph run artifacts, state/progress/handoff, and selected/next slice status updates.
