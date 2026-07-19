# Slice 012B: Register Exports

## Status
Not Started

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Goal
Add asynchronous, idempotent report/register export jobs with observable lifecycle, expiring
downloads, and deterministic files generated from the 012A report selectors.

## User Value
Authorised staff can request large registers without blocking the application, follow progress,
and download a reproducible file containing the exact filters they requested.

## Depends On
- 012A3

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_report_export_postgresql_acceptance.RegisterExportPostgreSQLAcceptanceTests`
- Expected tests: 1

## Source References
- `docs/source/api-contracts.md` sections 40.7-40.8 and 45 (export and idempotency contracts)
- `docs/source/product-requirements.md` section 11.31
- `docs/source/technical-architecture.md` sections 21.3-21.4
- `docs/source/codebase-design.md` sections 33.1 and 33.3
- `docs/source/test-plan.md` sections 22.1-22.2 and 24.1
- `docs/source/implementation-roadmap.md` sections 17.3 and Sprint 20
- `docs/working/digests/epic-012-reports-exports-hardening-uat.md` section 012B

## Prototype Reference
- sfpcl-lms/src/pages/reports/ReportsMIS.tsx
- sfpcl-lms/src/pages/registers/RegistersHub.tsx
- sfpcl-lms/src/pages/Dashboard.tsx

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
- Implement `POST /api/v1/reports/exports/` and
  `GET /api/v1/reports/exports/{export_job_id}/` with persisted
  `queued/running/completed/failed` state and standard error envelopes.
- Accept only registered 012A report codes, an explicit supported format, canonical filters, and
  the standard idempotency key. Actor + report + canonical filters + format + key identifies one
  job; replay returns that job and worker retry cannot create a second file.
- Generate exports asynchronously through a thin task wrapper over a tested export service.
  Reuse report selectors rather than querying business models independently.
- Produce a documented format/report matrix from the source-required XLSX/CSV/PDF/JSON set;
  reject unsupported combinations. Include generated-by, generated-at, report code, and applied
  filters in the file metadata/header.
- Issue short-lived download grants through the existing storage adapter; expose failure reason
  codes without stack traces. Define cleanup/retention for expired jobs and files.

## Database/Model Impact
Add a non-destructive report export job model only if no compatible job record exists: actor,
report code, canonical filters, format, idempotency key, state, timestamps, failure code, file
reference, checksum, expiry, and uniqueness needed to prevent duplicate active/replayed jobs.

## API Contracts
Match `api-contracts.md` 40.7-40.8 and the project idempotency/error conventions; document the
supported format matrix and all lifecycle states.

## Permissions
Require both access to the underlying report and `reports.export`. This slice does not grant
unmasked sensitive export; 012C hardens column/reason policy.

## Audit Requirements
Use the central audit adapter for export request and actual download, referencing the job/report
and outcome but never embedding exported values. Preserve denied/failed outcomes for 012C.

## Validation Rules
- Only valid forward lifecycle transitions are allowed; terminal jobs cannot be rerun in place.
- Canonical filters used by the selector, stored job, status response, and file must agree.
- Download grants expire and cannot expose a raw permanent object-storage URL.
- Export work is asynchronous whenever generation exceeds the source five-second target.

## Test Cases
- TDD service/API tests for request, every state, invalid report/format/filter, failed generation,
  missing job, expired download, and 401/403.
- Replay and concurrent-duplicate tests prove one job/file; worker retry/restart resumes safely.
- File-level tests parse each supported format and reconcile rows/filters with 012A selectors,
  including generated-by/time metadata.
- Reverse-consumer tests cover storage signed URLs, task retry, audit calls, report permissions,
  and unchanged synchronous report reads.

## Visual Acceptance Criteria
None.

## Evidence Required
RED/GREEN evidence; job lifecycle API examples; supported-format matrix; parsed-file row/checksum
evidence; idempotency/concurrency/retry output; expiry and permission negatives; full gate.

## Non-Goals
Sensitive unmasking policy (012C), report/audit frontend wiring (012DA), scheduled email, saved
report views, or rebuilding business-domain report queries.

## Risk Level
Medium

## Acceptance Criteria
- Registered reports export asynchronously through one idempotent job per request identity, with
  status, reproducible file contents, failure handling, and expiring downloads.
- Files reconcile to 012A selectors and contain applied-filter/generator metadata.
- Request/download audits contain no result data; underlying read plus export permission is
  required.
- Sensitive unmasking policy, UI wiring, scheduled email, and saved views remain out of scope.

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
- [ ] Substantive unresolved risk or decision recorded only if needed
- [ ] Commit created only after passing gates
