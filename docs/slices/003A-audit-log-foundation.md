# Slice 003A: Audit Log Foundation

## Status
Not Started

## Parent Epic
Epic 003: Audit, Documents, Config, and Dashboard Foundation
Epic file: `docs/epics/003-audit-documents-config-foundation.md`

## Goal
Expose the existing append-only `AuditLog` records through a protected, paginated
backend API so future workflow and document slices can render audit timelines without
duplicating audit serialization.

## User Value
Authorized staff can retrieve a consistent audit trail for an entity or actor, and future
UI/API slices can rely on a standard audit response item shape.

## Depends On
- 002K

## Source References
- docs/source/implementation-roadmap.md sections 10, 20-22
- docs/source/api-contracts.md sections 26, 39, 41, 42-43
- docs/source/data-model.md document/config/audit tables
- docs/source/component-spec.md
- docs/source/design-system.md

## Prototype Reference
- sfpcl-lms/src/pages/Dashboard.tsx
- sfpcl-lms/src/pages/tasks/TaskInbox.tsx
- sfpcl-lms/src/components/loan/AuditTimeline.tsx
- sfpcl-lms/src/components/loan/DocumentPackModal.tsx

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
1. Add `GET /api/v1/audit-logs/` as a read-only protected endpoint over the existing
   `identity.AuditLog` model. Do not create a new audit table in this slice.
2. Support narrow filters from `api-contracts.md` §42.1: `entity_type`,
   `entity_id`, and `actor_user_id`. Unknown filters should return `400 VALIDATION_ERROR`
   through the standard error envelope.
3. Return newest-first paginated results using the existing top-level `pagination`
   contract and the 002J pagination helper in tests.
4. Serialize each item with the §42.1 fields available today: `audit_log_id`,
   `actor{user_id, full_name}` when present, `actor_type`, `action`, `entity_type`,
   `entity_id`, `old_value`, `new_value`, `ip_address`, and `created_at`. If the current
   model field names are `old_value_json`/`new_value_json`, map them to the contract names
   `old_value`/`new_value` in the API response.
5. Keep writes append-only by service/API convention: this slice adds no update/delete
   endpoint for audit rows.

## Database/Model Impact
No schema change expected. If a missing index is discovered, add at most one
non-destructive migration for query support; otherwise use the existing `AuditLog` model.

## API Contracts
Update `docs/working/API_CONTRACTS.md` with the concrete `GET /api/v1/audit-logs/`
contract, filter rules, permission rule, and example response.

## Permissions
Require session-bound bearer auth and a canonical audit/report/admin permission already in
the seeded catalogue, preferring `reports.audit.read` if present. If no exact source-backed
permission code exists in the catalogue, record an assumption and use the narrowest
existing read/audit permission; do not invent a new permission code in this slice.

## Audit Requirements
The read endpoint itself does not create a new audit row unless source docs explicitly
require read-auditing for audit-log access. It must preserve existing auth/admin/tracer
audit rows exactly and must not mutate returned audit records.

## Validation Rules
- Missing bearer token returns 002J-validated `401 AUTH_REQUIRED`.
- Invalid/revoked session returns 002J-validated `401 INVALID_TOKEN`.
- Authenticated user without the selected audit-read permission returns 002J-validated
  `403 PERMISSION_DENIED`.
- Invalid UUID filters return `400 VALIDATION_ERROR` with `field_errors`.
- Empty result sets return `success: true`, `data: []`, and valid pagination metadata.

## Test Cases
- Backend TDD: unauthenticated audit-log list fails first with missing endpoint or
  non-standard envelope, then passes with `401 AUTH_REQUIRED` using the 002J helper.
- Backend API: authorized user can list seeded/auth-generated audit rows with §42.1 item
  fields and valid top-level pagination.
- Backend API: `entity_type` + `entity_id` filters return only matching audit rows.
- Backend API: `actor_user_id` filter returns only that actor's audit rows.
- Backend API: user without the audit-read permission receives standard `403
  PERMISSION_DENIED`.
- Backend API: invalid UUID filter returns `400 VALIDATION_ERROR` with field errors.

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
