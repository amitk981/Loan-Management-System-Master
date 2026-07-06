# Slice 002C: Role and Permission Catalogue Seed

## Status
Complete

## Parent Epic
Epic 002: Platform Auth and Role Shell
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Seed the backend role, team, and permission catalogue needed by the auth shell, using Epic 002's distilled auth-permissions requirements as the source for canonical codes.

## User Value
Administrators and future APIs can rely on stable role/permission codes instead of prototype-only permission strings.

## Depends On
- 002B2

## Concrete Requirements
1. Add backend `Permission` and `RolePermission` models, plus a non-destructive migration, if they do not already exist.
2. Seed the permission catalogue using canonical module/verb codes from the Epic 002 digest: auth/user-admin, members, KYC, applications, credit assessment, approvals, documentation, security, SAP/finance, monitoring/default, closure, compliance, reports/audit/config.
3. Seed standard internal roles from the digest: Field Officer, Deputy Manager-Finance, Credit Manager, Compliance Team Member, Company Secretary, Senior Manager-Finance, Chief Financial Controller, CFO, Director, Accounts Head, Sales Team User, IT Head, Internal Auditor, System Administrator.
4. Include external/future role records as inactive or clearly non-MVP where appropriate: Borrower/Member, Nominee, Bank User, Subsidiary User, External Auditor.
5. Seed team types from the digest: Credit Assessment, Compliance, Treasury, Sanction Committee, Accounts, IT, Audit, Sales.
6. Reconcile prototype permission aliases recorded in `docs/working/ASSUMPTIONS.md` A-005: map or replace `export`, `export_reports`, and `view_loans` with canonical backend permission codes.
7. Make seed execution idempotent so rerunning it does not duplicate roles, teams, permissions, or role-permission links.

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
Implement catalogue models and an idempotent seed command/service. Keep seed behavior behind an explicit module or management-command boundary so reruns, tests, and later admin APIs do not duplicate catalogue logic. No public admin API is required in this slice unless needed for verification.

## Database/Model Impact
Non-destructive model/migration changes for this capability, if needed.

## API Contracts
Update `docs/working/API_CONTRACTS.md` only if a verification endpoint is added. Otherwise note that this slice is database/seed only.

## Permissions
Use the digest role catalogue and permission module list. Unknown permissions must not be invented; record gaps in `docs/working/ASSUMPTIONS.md`.

## Audit Requirements
No runtime audit event is required for initial seed data. If a seed command mutates existing records, print a non-secret summary only.

## Validation Rules
Role codes, team codes, and permission codes are unique. Seed data must be deterministic and idempotent.

## Test Cases
- New test: seed command creates the expected standard internal role codes and team codes from the digest.
- New test: seed command creates representative permission codes across each digest module group.
- New test: rerunning the seed command is idempotent and does not duplicate catalogue rows.
- New test: prototype alias reconciliation from A-005 is represented in canonical permission data or the assumption is updated as resolved/deferred.
- New test: role-permission seed data is created through the same seed module/interface the command uses, not by duplicating setup logic inside the test.

## Visual Acceptance Criteria
None.

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched.

## Risk Level
High

## Acceptance Criteria
- Role, team, permission, and role-permission catalogue data can be loaded in a fresh database.
- Canonical catalogue codes are stable, unique, and tested.
- A-005 is resolved or explicitly carried forward with a concrete follow-up.
- The implementation stays within one small Ralph slice.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated, if needed (n/a — DB/seed only; noted in API_CONTRACTS)
- [x] Database rules followed, if needed
- [x] Permissions tested, if needed
- [x] Audit events tested, if needed (n/a — no runtime audit for initial seed)
- [x] Visual evidence saved, if frontend (n/a — no frontend change)
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [x] Commit created only after passing gates (orchestrator commits)
