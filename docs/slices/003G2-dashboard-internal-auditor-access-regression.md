# Slice 003G2: Dashboard Internal Auditor Access Regression

## Status
Not Started

## Parent Epic
Epic 003: Audit, Documents, Config, and Dashboard Foundation
Epic file: `docs/epics/003-audit-documents-config-foundation.md`

## Goal
Fix the 003G dashboard permission/catalogue mismatch for the `internal_auditor` dashboard role
context before the frontend dashboard is wired to the API.

## User Value
Internal auditors get the compliance dashboard shell that the documented 003G role-context mapping
promises, instead of receiving a backend `403` once the UI is API-backed.

## Depends On
- 003G

## Source References
- docs/source/api-contracts.md section 43
- docs/source/functional-spec.md sections 12.2-12.6
- docs/source/auth-permissions.md section 19.1
- docs/working/ASSUMPTIONS.md A-023
- docs/working/digests/epic-003-audit-documents-config.md dashboard extracts

## Prototype Reference
- sfpcl-lms/src/pages/Dashboard.tsx

## Screens Involved
None directly. This is a backend/API regression slice that must complete before 003H UI wiring.

## Frontend Scope
None.

## Backend/API Scope
1. Preserve the existing 003G `GET /api/v1/dashboard/` response contract:
   `data.role_context`, `data.cards[]`, and `data.tasks[]`.
2. Add a failing-first regression proving an authenticated `internal_auditor` receives
   `role_context: "compliance"` from `/api/v1/dashboard/` when the seeded catalogue is used.
3. Update the canonical catalogue seed so `internal_auditor` receives the source-backed
   `management_readonly` dashboard scope described in A-023, or if source review rejects auditor
   dashboard access, remove `internal_auditor` from the 003G role-context mapping and revise A-023.
4. Extend the catalogue seed regression so every role named in the 003G role-context mapping has
   the permission needed to reach its mapped dashboard context.
5. Do not add dashboard calculations, specialist dashboard endpoints, task persistence, frontend
   wiring, or new role-specific business rules.

## Database/Model Impact
No schema change. Catalogue seed data only.

## API Contracts
Update `docs/working/API_CONTRACTS.md` only if the role-context mapping changes. If the fix is a
seed grant, the 003G contract remains unchanged.

## Permissions
Use `management_readonly` only. Do not invent `dashboard.read` or reuse report/export permissions.

## Audit Requirements
Dashboard reads remain read-only and must not create `AuditLog` rows.

## Validation Rules
No query parameters remain supported. Unknown query parameters still return standard
`400 VALIDATION_ERROR`.

## Test Cases
- Red/green: seeded `internal_auditor` can access `/api/v1/dashboard/` and receives
  `role_context: "compliance"`.
- Catalogue regression: all roles named in `sfpcl_credit.dashboard.services._ROLE_CONTEXTS` that
  are expected to be dashboard-capable have `management_readonly` after `seed_catalogue()`.
- Existing 003G tests for other contexts, `401`, `403`, unknown query params, and no audit rows
  remain green.

## Visual Acceptance Criteria
None.

## Evidence Required
Red/green backend test output and full quality gates.

## Risk Level
Medium

## Acceptance Criteria
- The internal-auditor dashboard mapping is reachable or explicitly removed from the documented
  mapping.
- Tests cover the catalogue/role-context consistency that 003G missed.
- No production dashboard calculations or frontend UI changes are introduced.

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
