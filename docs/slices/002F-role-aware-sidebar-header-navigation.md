# Slice 002F: Role-Aware Sidebar Header Navigation

## Status
Not Started

## Parent Epic
Epic 002: Platform Auth and Role Shell
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Deliver this narrow capability as a small, testable Ralph implementation slice.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 002E
- 002E2
- 002EX

## Source References
- docs/source/implementation-roadmap.md sections 10, 20-22
- docs/source/technical-architecture.md sections 8-12, 17-18
- docs/source/auth-permissions.md
- docs/source/api-contracts.md sections 11-12, 43-44
- docs/source/data-model.md identity/access tables

## Prototype Reference
- sfpcl-lms/src/pages/auth/LoginScreen.tsx
- sfpcl-lms/src/pages/Dashboard.tsx
- sfpcl-lms/src/components/layout/*
- sfpcl-lms/src/contexts/RoleContext.tsx

## Screens Involved
Relevant prototype screen area for this capability.

## Frontend Scope
- Verify and close any remaining sidebar/header affordances after 002E/002E2/002EX.
- Navigation visibility must derive only from explicit prototype permissions mapped from backend canonical permissions.
- `backend_staff`, `it_head`, `management_viewer`, unknown roles, and empty-permission sessions must see only unrestricted shell content and no Tracer, Settings, auditor/admin/borrower shortcuts, or action buttons.
- `tracer.lifecycle.run` maps only to the Tracer navigation/action; it must not unlock member, finance, audit, report, or settings pages.

## Backend/API Scope
No new backend capability unless a missing permission/action contract is discovered. If backend changes are needed, keep them to `/auth/me/` action availability or explicit permission seed/test setup and update `API_CONTRACTS.md`.

## Database/Model Impact
None.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Apply the 002D3 `/auth/me/` contract (`roles`, `teams`, `permissions`, `available_actions`) and the 002E2 neutral-role rule. Unknown canonical permissions and unknown role codes grant no prototype UI access unless this slice maps them explicitly with tests and an `ASSUMPTIONS.md` entry.

## Audit Requirements
Record audit/workflow events for critical create/update/approval/access actions.

## Validation Rules
Enforce source-doc business rules and block invalid state transitions.

## Test Cases
- Frontend tests prove canonical permissions map to exactly the expected prototype permissions, including `tracer.lifecycle.run -> run_tracer`.
- Empty-permission `credit_manager`, `it_head`, `management_viewer`, and unknown role-code responses do not expose protected sidebar items or header shortcuts.
- A staff user with only `tracer.lifecycle.run` sees Tracer but not Applications, Members, Loan Accounts, Reports, Settings, or Audit.
- Logout/revoked-session restore path returns to staff login before protected navigation is rendered.

## Visual Acceptance Criteria
Match the existing prototype patterns and include loading, empty, error, unauthorized, validation, and success states where relevant.

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
