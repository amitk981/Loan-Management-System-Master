# Slice 003L: Data Import and Migration Planning

## Status
Complete

## Parent Epic
Epic 003: Audit, Documents, Config, and Dashboard Foundation
Epic file: `docs/epics/003-audit-documents-config-foundation.md`

## Goal
Create a source-backed data import and migration planning artifact for future member, loan,
document, audit/config, communication, and reporting data loads without importing real data or
writing migration tooling yet.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 003K

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
Docs/planning only unless a validation fixture is required. Produce a migration planning document
under `docs/working/` that maps:
- Source system/data-area candidates from the already implemented foundations: users/roles/teams,
  document file metadata, audit logs/workflow events, loan policy configs/version histories,
  content templates, communications, notifications, dashboard shells, and scheduled job metadata.
- Future high-volume/business tables called out by source docs: members/KYC/shareholding,
  applications/appraisals/approvals, loan accounts/repayments/interest/DPD/reminders/MIS,
  securities, compliance trackers, reports/export jobs.
- Required import controls: dry-run mode, row-level validation, idempotency/natural keys, error
  summaries, auditability, rollback/retry plan, sensitive-data masking, and no real personal or
  financial data in tests.
- How `scheduled_jobs` from 003J may be used later to track async import batches or export jobs,
  while this slice must not enqueue real jobs or add workers.
- Current prototype/API status from 003K: Dashboard, Notifications Center, and My Profile are
  API-backed; Task Inbox, AuditTimeline, and DocumentPackModal remain mock/prototype shells. The
  migration plan must not claim that task inbox data, dashboard task generation, document pack
  generation, or audit timeline UI wiring exists yet.
- Import plan outputs should separate existing foundation tables from future business tables:
  existing foundations can be mapped to concrete implemented models/APIs, while future member,
  application, loan, repayment, default, closure, compliance, and report tables should be listed as
  target areas only until their owning slices create schema and contracts.

## Database/Model Impact
None. Do not add import staging tables in 003L; create follow-up implementation slices if the plan
identifies required tables.

## API Contracts
None, unless this planning/test slice discovers a contract gap to document.

## Permissions
Planning must identify that future import execution is administrative/high-control work. If exact
source permission codes are absent, record the gap in `ASSUMPTIONS.md`; do not reuse communication,
dashboard, or report-export permissions for import administration.

## Audit Requirements
Planning must require audit records for import batch start, validation failure summary, commit,
rollback/cancel, and sensitive data reveal/export during migration review. Do not log raw file
payloads or full sensitive values.

## Validation Rules
Planning must list validation categories rather than inventing business rules: UUID/business-key
dedupe, required fields, reference integrity, status enum mapping, date/timezone normalization,
money precision, document checksum/storage-key presence, and permissioned handling of sensitive
fields.

## Test Cases
Docs/protected-path checks plus standard gates. If planning creates structured examples, include
test-safe synthetic rows only and verify no real personal or financial data is committed. Include a
manual traceability note in the review packet that 003J `scheduled_jobs` is metadata-only and that
003K still classifies Task Inbox as prototype/mock.

## Visual Acceptance Criteria
None.

## Evidence Required
Updated migration planning artifact, gate logs, changed-files list, and review packet. No API
response examples or screenshots are required unless code/frontend is touched.

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
