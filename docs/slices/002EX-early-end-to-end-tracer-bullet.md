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
- 002D2 (persistent dev DB and CORS-backed frontend/backend stitching)

## Concrete Requirements
1. Skeleton models with MINIMAL fields only (id, reference, status, amount, member link, timestamps): Member, LoanApplication, LoanAccount, Repayment. Later slices (004x, 005x, 009x, 010x) own the real field sets — do not anticipate them.
2. Status transitions go through the state-machine/transition-guard pattern (002H may not exist yet — implement the minimal guard inline in the service layer and note it for 002H).
3. One API endpoint per transition, named per `docs/source/api-contracts.md` conventions; record each contract in `docs/working/API_CONTRACTS.md`.
4. Every transition writes an audit event.
5. Frontend: one simple "Tracer" screen (dev-only route is acceptable) that drives the happy path against the real API — not mock data.
6. No business rules beyond "amounts must be positive and status transitions must follow the sequence". Do not invent eligibility, interest, or document logic.
7. The tracer must run as an authenticated staff user using the 002E session state. Do not bypass auth with fixture-only endpoints.
8. Use the persistent development SQLite database from 002D2 for manual/dev smoke evidence, but keep automated backend tests on Django's migrated test database.

## Test Cases
- One scripted end-to-end test (API level) walking the full path: create member → application → sanction → account → disbursement → repayment → closure.
- Each transition rejects an out-of-order call (e.g., disburse before sanction).
- Auth regression: an unauthenticated request to at least one tracer endpoint returns the standard `401` envelope and does not write domain/audit rows.

## Evidence Required
- API response samples for each transition.
- Screenshot of the tracer screen after closure.
- Risk assessment listing which controls are intentionally deferred.
- Dev smoke note showing data remains available after separate requests against `sfpcl_credit/db.sqlite3`.

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
