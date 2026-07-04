# Slice 002G2: Admin User Action Permission Granularity

## Status
Not Started

## Parent Epic
Epic 002: Platform Auth and Role Shell
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Tighten the 002G admin user-management backend so read, update, and disable actions are gated by the appropriate canonical user-admin permission instead of treating any one user-admin permission as full authority.

## User Value
A future staff role with limited user-admin authority cannot accidentally suspend users or change role/team assignments merely because it has one unrelated user-admin permission.

## Depends On
- 002G

## Review Finding
Created by architecture review `2026-07-04_135247_architecture_review`.

## Concrete Requirements
1. Replace the single broad `has_manage_users_permission()` gate with action-aware backend permission checks.
2. Preserve current `system_admin` access using the permissions actually seeded today (`users.user.create`, `users.user.update`, `users.user.disable`) unless source documents are corrected in the same slice.
3. Gate role assignment and team membership changes with `users.user.update`.
4. Gate status changes to `suspended` with `users.user.disable`; status restoration to `active` may use `users.user.update` unless source docs say otherwise.
5. List/detail read access must be explicitly decided from source: prefer `users.user.read` because `auth-permissions.md` §12.1 defines it and §19 routes `/settings/users` to it; if `system_admin` still lacks that seed grant, record the compatibility assumption and keep list/detail reachable only to a clearly documented user-admin permission set.
6. Frontend route/nav visibility may continue using prototype `manage_users`, but action buttons must not imply authority the backend will reject. If frontend action visibility is changed, reuse existing UI patterns only and save visual evidence.
7. Add backend regression tests with deliberately partial roles:
   - a role with only `users.user.create` cannot assign roles, change teams, or suspend users;
   - a role with only `users.user.update` can change role/team assignments but cannot suspend users;
   - a role with only `users.user.disable` can suspend users but cannot assign roles or teams;
   - a user lacking the required action permission receives `403 PERMISSION_DENIED` and no audit/session mutation occurs.
8. Keep the 002G last-active-`system_admin` lock-out guard and session revocation behavior unchanged.
9. Save red/green evidence under `.ralph/runs/<run-id>/evidence/terminal-logs/` and include API examples for at least one partial-permission `403`.

## Source / Digest References
- `docs/source/auth-permissions.md` §12.1: `users.user.read`, `users.user.create`, `users.user.update`, and `users.user.disable` are distinct risk-rated permission codes.
- `docs/source/auth-permissions.md` §15.12: System Administrator key permissions include create/update/disable plus role/config administration.
- `docs/source/auth-permissions.md` §19 route mapping: `/settings/users` maps to `users.user.read`.
- `docs/working/digests/epic-002-platform-auth.md` entry from architecture review `2026-07-04_135247`.

## Test Cases
- Backend TDD: partial user-admin roles fail closed for actions they do not explicitly hold.
- Backend regression: the seeded `system_admin` path used by 002G still passes list/detail/assignment/status tests.
- Backend regression: forbidden partial-permission writes do not create `AuditLog` rows and do not revoke target sessions.
- Frontend regression, if touched: Admin Users nav remains hidden from zero-permission, unknown-role, and tracer-only sessions.

## Risk Level
High

## Acceptance Criteria
- Backend user-admin endpoints enforce action-specific permission checks.
- No current `system_admin` workflow regresses.
- Permission-denied and success cases are covered by behavior tests and saved evidence.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written first
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Permissions tested
- [ ] Audit/session side effects tested
- [ ] Visual evidence saved, if frontend is touched
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
