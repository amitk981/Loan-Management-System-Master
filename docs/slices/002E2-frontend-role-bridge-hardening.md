# Slice 002E2: Frontend Role Bridge Hardening

## Status
Not Started

## Parent Epic
Epic 002: Platform Auth and Role Shell
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Remove the unsafe frontend role fallback introduced by the 002E backend-auth bridge before tracer and role-aware navigation work builds on it.

## User Value
Staff users whose backend role is not yet mapped in the prototype do not accidentally see auditor/admin/borrower-shaped dashboard content or actions.

## Depends On
- 002E

## Source References
- `docs/source/auth-permissions.md` §13.1 role catalogue
- `docs/source/implementation-roadmap.md` §10.6 R1-AC-004 and R1-AC-005
- `docs/source/api-contracts.md` §11.4 and closing implementation rule
- `docs/working/digests/epic-002-platform-auth.md`
- Architecture review finding: `2026-07-03_224536_architecture_review`

## Concrete Requirements
1. Replace `mapBackendUserToFrontendUser()`'s `mappedRole ?? 'auditor'` fallback with a neutral, no-affordance path. Do not fall back to `auditor`, `admin`, `borrower`, or any role that has role-specific dashboard/profile/action branches.
2. Add explicit handling for every backend role code that can be returned by the seeded catalogue, including `it_head` and `management_viewer`. If a backend role does not have a prototype role equivalent yet, it must retain backend display labels and role codes while receiving no prototype permissions unless canonical backend permissions map explicitly.
3. Audit direct `currentUser.role` branches touched by the protected shell (`Dashboard`, `MyProfile`, header/sidebar route access, and any shell-level role display) so unmapped or zero-permission backend roles do not inherit auditor-specific widgets, sensitive-profile affordances, or action labels.
4. Keep route/sidebar visibility driven by canonical backend permissions through the explicit mapping layer from 002E. Unknown canonical permissions must still grant no UI access and remain recorded in `ASSUMPTIONS.md` if they affect a visible screen.
5. Preserve borrower portal demo auth and the `VITE_ENABLE_DEMO_AUTH` staff demo path.
6. Do not add new styling. Use existing dashboard/profile empty/blocked patterns if a neutral backend staff state needs copy.

## Frontend Scope
- `sfpcl-lms/src/services/authSession.ts`
- `sfpcl-lms/src/contexts/RoleContext.tsx`
- Protected-shell role-specific display branches as needed
- Focused tests for role mapping and permission-gated shell behavior

## Backend/API Scope
None.

## Test Cases
- Frontend unit test: backend `it_head` with no permissions maps to backend display labels/role codes but not to `auditor`, `admin`, or `borrower`.
- Frontend unit test: backend `management_viewer` with no permissions receives no prototype permissions and no route/action visibility beyond unrestricted shell access.
- Frontend regression: a zero-permission backend staff session cannot see auditor-specific dashboard/profile affordances or permission-gated navigation.
- Existing 002E auth-session tests remain green.

## Evidence Required
- TDD red/green frontend test logs.
- Frontend full tests, typecheck, and build logs.
- Backend gates still green or documented as unchanged if the orchestrator permits a frontend-only gate subset.
- Review packet must cite the architecture-review finding this slice closes.

## Risk Level
Medium

## Acceptance Criteria
- Unmapped backend roles no longer receive auditor/admin/borrower behavior by default.
- Permission-gated navigation and actions remain driven by backend canonical permissions.
- 002EX can safely add tracer permissions without inheriting the 002E fallback defect.
- All configured gates pass.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Permissions tested
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
