# Slice 002EX: Early End-to-End Tracer Bullet

## Status
Not Started

## Parent Epic
Epic 002: Platform Auth and Role Shell (integration proof)
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Prove the whole architecture connects — React frontend → API → Django service layer → database → back — by pushing ONE loan through a minimal skeleton of the full life cycle. This is deliberately thin: it validates the plumbing early so that structural problems surface now, not after 50 slices.

## User Value
A logged-in staff user can create a member, create a loan application for them, record a sanction decision, create a loan account, mark a disbursement, post one repayment, and close the loan — all persisted, all audited, all visible in the UI.

## Depends On
- 002E (login + protected frontend shell)
- 002E2 (neutral frontend role bridge for unmapped/zero-permission backend roles)
- 002D2 (persistent dev DB and CORS-backed frontend/backend stitching)
- 002D3 (source-fidelity `/auth/me/` profile, roles, teams, and permissions shape)

## Concrete Requirements
1. Skeleton models with MINIMAL fields only (id, reference, status, amount, member link, timestamps): Member, LoanApplication, LoanAccount, Repayment. Later slices (004x, 005x, 009x, 010x) own the real field sets — do not anticipate them.
2. Status transitions go through the state-machine/transition-guard pattern (002H may not exist yet — implement the minimal guard inline in the service layer and note it for 002H).
3. One API endpoint per transition, named per `docs/source/api-contracts.md` conventions; record each contract in `docs/working/API_CONTRACTS.md`.
4. Every transition writes an audit event.
5. Frontend: one simple "Tracer" screen (dev-only route is acceptable) that drives the happy path against the real API — not mock data.
6. No business rules beyond "amounts must be positive and status transitions must follow the sequence". Do not invent eligibility, interest, or document logic.
7. The tracer must run as an authenticated staff user using the 002E session state. Do not bypass auth with fixture-only endpoints.
8. Use the persistent development SQLite database from 002D2 for manual/dev smoke evidence, but keep automated backend tests on Django's migrated test database.
9. The tracer UI must use the 002D3 `/auth/me/` session contract: display staff role/team names from `roles`/`teams`, use canonical `permissions`/`available_actions` for route/action visibility, and keep `role_codes`/`team_codes` only as compatibility data.
10. The frontend tracer route must sit behind the 002E protected staff shell: no tracer UI renders until `POST /api/v1/auth/login/` succeeds and `GET /api/v1/auth/me/` succeeds with an active session-bound bearer token.
11. Use 002E's local token/session storage and logout behavior unchanged. A revoked/logout session must send the user back to the staff login before any tracer action button is available.
12. Add only the minimum permission bridge entries needed for the tracer screen, and record any unmapped canonical backend permissions in `docs/working/ASSUMPTIONS.md` instead of granting broad prototype permissions.
13. Do not implement tracer UI on top of the 002E `auditor` fallback defect. The staff user used for tracer evidence must have an explicitly mapped backend role and explicit canonical permissions for tracer route/action visibility.
14. Preserve the 002E2 hardening behavior: backend roles with empty permissions, including `it_head` or `management_viewer`, must not see tracer navigation, tracer action buttons, or auditor-shaped dashboard shortcuts.

## Test Cases
- One scripted end-to-end test (API level) walking the full path: create member → application → sanction → account → disbursement → repayment → closure.
- Each transition rejects an out-of-order call (e.g., disburse before sanction).
- Auth regression: an unauthenticated request to at least one tracer endpoint returns the standard `401` envelope and does not write domain/audit rows.
- Auth regression: an authenticated tracer request with a revoked session access token returns `401 INVALID_TOKEN` using the standard envelope before any domain transition occurs.
- Frontend regression: a staff session with an empty `/auth/me/` `permissions` list cannot see or run the tracer actions.
- Frontend regression: an unmapped or zero-permission backend role does not inherit auditor/admin/borrower UI behavior while tracer permissions remain hidden.

## Evidence Required
- API response samples for each transition.
- Screenshot of the tracer screen after closure.
- Risk assessment listing which controls are intentionally deferred.
- Dev smoke note showing data remains available after separate requests against `sfpcl_credit/db.sqlite3`.
- Auth smoke note showing tracer evidence used the real 002E login → `/auth/me/` path, not the `VITE_ENABLE_DEMO_AUTH` fallback.
- Role-bridge smoke note showing the tracer user has explicit backend permissions and that a zero-permission backend role cannot reach tracer controls.

## Out of Scope
Exception paths, documents, interest, reports, compliance trackers, member portal.

## Risk Level
High

## Acceptance Criteria
- The full happy path runs against the real backend with data persisted between steps.
- All gates pass.
- `docs/working/MVP_TRACER_BULLET.md` updated with what was proven and what was deferred.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Audit events tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
