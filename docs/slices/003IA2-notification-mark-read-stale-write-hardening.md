# Slice 003IA2: Notification Mark-Read Stale-Write Hardening

## Status
Not Started

## Parent Epic
Epic 003: Audit, Documents, Config, and Dashboard Foundation
Epic file: `docs/epics/003-audit-documents-config-foundation.md`

## Goal
Harden the `POST /api/v1/notifications/{notification_id}/mark-read/` endpoint so the documented
`read_state_version` stale-write contract is enforced atomically under concurrent requests.

## User Value
Staff notification read state remains auditable and deterministic even if a user double-clicks,
opens the same inbox in two tabs, or retries a mark-read action while another request is in flight.

## Depends On
- 003IA

## Source References
- docs/source/screen-spec.md section 5.8 and screen S04
- docs/source/api-contracts.md section 8.1 and section 39 endpoint conventions
- docs/working/API_CONTRACTS.md notification mark-read contract
- docs/working/REVIEW_FINDINGS.md entry for 2026-07-06_183803_architecture_review

## Prototype Reference
- sfpcl-lms/src/pages/notifications/NotificationsCenter.tsx

## Screens Involved
Notifications Center only if client error handling needs a label-only correction. Do not redesign
or introduce new styling.

## Frontend Scope
None by default. If the backend returns `409 STALE_WRITE`, preserve the existing error/refresh
pattern or make only a label-only correction using current alert patterns.

## Backend/API Scope
1. Add a failing-first regression that demonstrates two same-version mark-read attempts cannot both
   persist/audit as successful updates.
2. Move stale-write enforcement into one atomic backend operation using the existing
   current-user recipient scope. Accept either a row lock (`select_for_update` inside
   `transaction.atomic`) or a conditional update that includes `notification_id`, recipient scope,
   and `read_state_version`.
3. Preserve existing `404 NOT_FOUND` behavior for notifications outside the current user's direct,
   active-role, or active-team scope.
4. Preserve existing `409 STALE_WRITE` response code when the submitted `read_state_version` does
   not match the persisted version.
5. Ensure a successful first mark-read writes exactly one
   `communications.notification.marked_read` audit row; a stale same-version retry writes no
   additional audit row and does not change `read_at`, `read_by_user`, or `read_state_version`.

## Database/Model Impact
No schema change expected.

## API Contracts
The existing contract remains unchanged unless implementation exposes a documented ambiguity. If
text is clarified, update `docs/working/API_CONTRACTS.md` in the same run.

## Permissions
Continue using `communications.notification.read` from A-026. Do not add a frontend-only
notification permission.

## Audit Requirements
Exactly one metadata-only `AuditLog` row per successful transition from unread to read. No audit row
for stale, forbidden, unauthenticated, or wrong-recipient attempts.

## Validation Rules
`read_state_version` remains required, positive, and the only accepted request body field. Unknown
fields return standard `400 VALIDATION_ERROR`.

## Test Cases
- Red/green backend regression: after one successful mark-read using version `1`, a second
  same-version call returns `409 STALE_WRITE`, leaves version `2`, and does not create a second
  audit row.
- Preserve existing tests for direct, role, and team recipient visibility.
- Preserve `401`, `403`, wrong-recipient `404`, invalid body `400`, and stale version `409` tests.
- Full backend tests, migration check, coverage, and frontend gates remain green.

## Visual Acceptance Criteria
None unless frontend copy is touched.

## Evidence Required
Red/green backend test output and full quality gates.

## Risk Level
Medium

## Acceptance Criteria
- The mark-read version check is atomic with the persisted update.
- Same-version retries cannot produce duplicate successful audit rows.
- The notification inbox contract and object-level scoping remain unchanged.

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
