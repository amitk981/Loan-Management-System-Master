# Slice 002F: Role-Aware Sidebar Header Navigation

## Status
Complete

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
- Sidebar (`sfpcl-lms/src/components/layout/Sidebar.tsx`) — 22 staff nav items,
  each gated by `requiredPermission` except `dashboard` (always shown).
- Header (`sfpcl-lms/src/components/layout/Header.tsx`) — profile menu (My Profile
  always; Settings only when `can('view_settings')`; Sign out), search results
  gated by `can('view_members'|'view_applications'|'view_loan_accounts')`, and the
  role-picker/notifications dropdowns.
- Route guard (`sfpcl-lms/src/App.tsx` `PAGE_PERMISSIONS` + `navigate`) — blocked
  pages fall back to the dashboard with the amber "Access blocked" banner.

## Concrete Requirements
1. Every `Sidebar` `requiredPermission` and every `App.tsx` `PAGE_PERMISSIONS`
   entry must be reachable only when the mapped prototype permission is present;
   add a frontend test that, for each nav item, a user lacking its
   `requiredPermission` does not see it and cannot navigate to it (the guard sends
   them to the dashboard with the blocked banner).
2. The canonical→prototype map lives in
   `sfpcl-lms/src/services/authSession.ts` (`CANONICAL_TO_PROTOTYPE_PERMISSIONS`);
   assert `tracer.lifecycle.run → run_tracer` is the ONLY mapping that unlocks
   Tracer, and that it unlocks nothing else (no members/finance/audit/reports/
   settings items). This is already partly covered by
   `authSession.test.ts` ("maps only the explicit tracer permission…") and the
   002EY Playwright `auth-negative` spec — extend, do not duplicate.
3. Neutral/zero-permission sessions (`backend_staff`, `it_head`,
   `management_viewer`, unknown role codes, empty `permissions`) render only
   `Dashboard` in the sidebar, no Settings shortcut in the profile menu, and no
   auditor/admin/borrower affordances. Reuse the 002EY `e2e.zero@sfpcl.example`
   seed for any browser assertion.
4. The logout / revoked-session restore path (`App.tsx`
   `restoreCurrentUserFromStoredSession` → `handleLogout`) must return to the
   staff `LoginScreen` before any protected sidebar/header item renders.
5. No design changes (FRONTEND_DESIGN_RULES.md): this slice only verifies and, if
   a genuine gap is found, tightens visibility/role logic on existing components.

## Frontend Scope
- Verify and close any remaining sidebar/header affordances after 002E/002E2/002EX/002EY.
- Navigation visibility must derive only from explicit prototype permissions mapped from backend canonical permissions (`can(permission)` in `RoleContext`, never role-name checks).
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
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated, if needed
- [x] Database rules followed, if needed
- [x] Permissions tested, if needed
- [x] Audit events tested, if needed
- [x] Visual evidence saved, if frontend
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates
