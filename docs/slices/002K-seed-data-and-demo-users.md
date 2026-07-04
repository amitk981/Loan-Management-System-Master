# Slice 002K: Seed Data and Demo Users

## Status
Not Started

## Parent Epic
Epic 002: Platform Auth and Role Shell
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Add a safe local/dev seed path for staff demo users that exercises the already-seeded role,
team, permission, admin-user, tracer, and auth contracts without weakening production seed
guards.

## User Value
The owner and future Ralph slices can log in with predictable local demo users that map to
real backend roles/teams/permissions, while production-like environments remain protected
from accidental predictable credentials.

## Depends On
- 002J

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
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
1. Add or extend a management command for local demo staff users only. Reuse existing
   `Role`, `Team`, `Permission`, `RolePermission`, `User`, and `UserTeamMembership`
   models; do not introduce new schema or free-text roles/permissions.
2. Require explicit local/dev guard flags before creating predictable credentials. Follow
   the 002EYA `seed_e2e_users` safety pattern: predictable users are allowed only when
   `SFPCL_DEBUG=true` and an explicit seed flag is present.
3. Seed a minimal set of demo staff accounts tied to already-defined active roles and
   teams, including at least: system administrator, credit manager, compliance user,
   treasury/finance user, internal auditor/read-only user, tracer-only user, and
   zero-permission neutral user.
4. Each seeded user must be idempotent: rerunning the command updates known demo users to
   the requested role/team/status/password but must not duplicate users, roles, teams, or
   memberships.
5. Seeded demo users must authenticate through the real `/api/v1/auth/login/` and
   `/api/v1/auth/me/` path; do not add demo-only auth bypasses.
6. Preserve 002G2 action-specific admin permissions and 002I object-scope conventions.
   Demo users must not receive broad permission aliases such as `manage_users`.

## Database/Model Impact
Non-destructive model/migration changes for this capability, if needed.

## API Contracts
No new public API endpoint expected. If demo login examples are documented, update
`docs/working/API_CONTRACTS.md` only as local-dev setup notes; do not change auth response
shapes.

## Permissions
Use only canonical backend permission codes from the seeded catalogue. Unknown role,
team, object, or permission needs must be denied or recorded in `ASSUMPTIONS.md`, not
invented.

## Audit Requirements
The seed command itself does not need production `AuditLog` rows. Login/logout with seeded
users must continue to create the existing auth audit rows.

## Validation Rules
- The command refuses to run without explicit local/dev guard flags.
- Reruns are idempotent and do not create duplicate users or duplicate memberships.
- Seeded users have active primary roles only when those roles already exist in the
  catalogue.
- Zero-permission demo user remains neutral in `/auth/me/` (`permissions: []`).
- Tracer-only demo user receives only `tracer.lifecycle.run` and no admin/user-management
  permissions.
- System administrator demo user preserves existing admin-shell access under 002G2
  action-specific rules.

## Test Cases
- Backend TDD: command refuses without guard flags.
- Backend TDD: guarded command creates the exact expected demo users, active memberships,
  and no duplicate rows on rerun.
- Backend regression: seeded system admin can login and call `/api/v1/auth/me/` with
  canonical user-admin permissions.
- Backend regression: seeded tracer-only user can login and has exactly
  `tracer.lifecycle.run`.
- Backend regression: seeded zero-permission user can login and has no permissions or
  prototype-derived grants.
- Backend regression: auth audit behavior still occurs through the existing login/logout
  path.

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
