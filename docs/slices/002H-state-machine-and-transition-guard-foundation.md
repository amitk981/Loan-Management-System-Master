# Slice 002H: State Machine and Transition Guard Foundation

## Status
Not Started

## Parent Epic
Epic 002: Platform Auth and Role Shell
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Introduce a small backend workflow transition guard module that later loan/member/document/security workflows can share, and migrate the existing tracer transition proof to use it without changing tracer endpoint behavior.

## User Value
Future workflow slices get one tested place for allowed-state checks, permission checks, audit/workflow-event metadata, and standard `409 INVALID_STATE_TRANSITION` errors instead of each endpoint hand-rolling state transitions.

## Depends On
- 002G

## Source References
- docs/source/implementation-roadmap.md sections 10, 20-22
- docs/source/technical-architecture.md sections 8-12, 17-18
- docs/source/auth-permissions.md
- docs/source/api-contracts.md sections 11-12, 43-44
- docs/source/data-model.md identity/access tables
- docs/source/domain-model.md (state machine and lifecycle terminology)

## Prototype Reference
- sfpcl-lms/src/pages/auth/LoginScreen.tsx
- sfpcl-lms/src/pages/Dashboard.tsx
- sfpcl-lms/src/components/layout/*
- sfpcl-lms/src/contexts/RoleContext.tsx

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
1. Add a backend workflow module interface (for example `sfpcl_credit/workflows/`) with typed transition definitions: entity type, from-state(s), to-state, required permission code, action code, and audit/workflow-event labels.
2. Add a service function that accepts the current state, requested action, and actor permissions, then returns the next state or raises explicit typed errors for unknown action, invalid current state, or missing permission.
3. Keep the module domain-neutral: do not encode loan eligibility, sanction authority, money amounts, or document completeness rules here.
4. Migrate only the existing tracer service transition map to call the shared guard, preserving the current tracer URLs, envelopes, statuses, audit logs, workflow events, and tests.
5. Reuse the existing standard error envelope translation for `401`, `403 PERMISSION_DENIED`, and `409 INVALID_STATE_TRANSITION`; do not add a frontend screen.

## Database/Model Impact
No schema change expected. If the guard needs durable metadata, stop at in-code definitions for this slice and record a follow-up rather than adding broad workflow tables.

## API Contracts
No new public endpoint expected. Update `docs/working/API_CONTRACTS.md` only if tracer error details or examples are clarified; endpoint paths and response shapes must remain compatible with 002EX.

## Permissions
Apply the role and object-access rules from `docs/source/auth-permissions.md`; classify unknown access as approval-required.

## Audit Requirements
Record audit/workflow events for critical create/update/approval/access actions.
- The migrated tracer path must still write one audit log and one workflow event per successful transition.
- Invalid transitions and permission denials must not create success audit/workflow events.

## Validation Rules
Enforce source-doc business rules and block invalid state transitions.
- Guard module tests cover allowed transition, invalid source state, unknown action, missing permission, and no-op/error behavior.
- Tracer API regression tests prove the existing `409 INVALID_STATE_TRANSITION`, `403 PERMISSION_DENIED`, and successful transition behavior remains unchanged after migration.

## Test Cases
Unit/service/API/permission tests plus frontend tests where UI is touched.
- Backend TDD: write failing unit tests for the shared guard before implementation.
- Backend regression: existing tracer API tests continue to pass, plus at least one test proving invalid transitions produce the same `409 INVALID_STATE_TRANSITION` envelope after the shared guard is introduced.

## Visual Acceptance Criteria
None.

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched.

## Risk Level
Medium

## Acceptance Criteria
- The named capability works through the intended backend/API/frontend path, where applicable.
- Source-doc business rules are enforced or documented as assumptions.
- Permissions and audit expectations are tested when applicable.
- The implementation stays within one small Ralph slice.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested, if needed
- [ ] Audit events tested, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
