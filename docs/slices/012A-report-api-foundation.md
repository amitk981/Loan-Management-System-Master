# Slice 012A: Report API Foundation

## Status
Complete

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Goal
Establish the read-only reporting boundary and implement the six source-contracted report
endpoints with deterministic filtering, pagination, role scope, and reconciliation to existing
domain records.

## User Value
Authorised staff can obtain trustworthy operational and portfolio reports directly from the
system of record instead of maintaining duplicate spreadsheets.

## Depends On
- 011O

## Runtime Capabilities

- `none`

## Source References
- `docs/source/product-requirements.md` section 11.31 (system-data reports, role-based list,
  reconciliation)
- `docs/source/api-contracts.md` sections 8 and 40.1-40.6 (list conventions and report routes)
- `docs/source/implementation-roadmap.md` sections 17.1-17.3 and Sprint 20
- `docs/source/information-architecture.md` section 16 (report catalogue and CFO MIS)
- `docs/source/technical-architecture.md` sections 21.1-21.3 (dashboard users and read models)
- `docs/source/codebase-design.md` sections 8.2 and 33.1-33.2 (reports app and selectors)
- `docs/source/test-plan.md` section 22.1
- `docs/working/digests/epic-012-reports-exports-hardening-uat.md` section 012A

## Prototype Reference
- sfpcl-lms/src/pages/reports/ReportsMIS.tsx
- sfpcl-lms/src/pages/registers/RegistersHub.tsx
- sfpcl-lms/src/pages/Dashboard.tsx

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
- Create/reuse a `reports` app boundary with a registry mapping stable report codes to
  report-specific, read-only selectors; do not put cross-domain query logic in views.
- Implement `GET` endpoints for application pipeline, documentation readiness, disbursement
  pending, loan portfolio, DPD, and compliance dashboard exactly as `api-contracts.md` 40.1-40.6.
- In the required-report catalogue, the application-pipeline selector is the Loan Request Register,
  documentation readiness is the Documentation Readiness Report, loan portfolio is the Loan
  Register, and DPD is the DPD Report. Disbursement Pending and Compliance Dashboard remain the two
  additional fixed section-40 APIs; neither is an alias for SAP Pending or the full Disbursement
  Report owned by 012A2.
- Support the contracted filters (`from_date`, `to_date`, `status`, `stage`, `as_of_date`,
  `sop_bucket`, `financial_year`), the standard response envelope/pagination, and deterministic
  ordering. Invalid dates, ranges, and controlled values return the standard 400 error.
- Apply report permission and object/team scope server-side. Empty authorised results return an
  empty page; unauthorised access returns 403 without disclosing totals.
- Reconcile rows/totals with seeded records from the owning application, documentation,
  disbursement, loan, monitoring, and compliance modules.

## Database/Model Impact
None expected. Prefer selectors over duplicated report tables or materialized views; record a
measured query problem before proposing a later optimisation.

## API Contracts
Implement and document the exact endpoints in `docs/source/api-contracts.md` 40.1-40.6 without
inventing export, scheduling, or saved-view fields.

## Permissions
Map each report to an existing `reports.*.read` permission and object/team scope. Where the source
has no report-specific code, require the owning resource's read permission and record the bounded
mapping assumption; default deny rather than inventing a broad grant. Management and auditor roles
remain read-only; no caller-supplied role may change the result scope.

## Audit Requirements
Ordinary report reads follow existing access logging policy and create no business workflow
event. Do not emit audit rows that include report result data or sensitive filter values.

## Validation Rules
- Report data is derived only from persisted source-domain records and preserves their canonical
  identifiers/statuses; selectors do not recompute or mutate business state.
- Dates use the project timezone and inclusive range semantics documented in the API contract;
  ordering is stable across pages.
- Query counts are bounded and list responses never return unpaginated high-volume rows.

## Test Cases
- TDD selector and API tests for every endpoint, each supported filter, combined filters,
  pagination/order, invalid values, empty results, 401, 403, and cross-team/object isolation.
- Reconciliation fixtures prove endpoint totals and rows equal the records held by each owning
  module, including boundary dates and DPD buckets.
- Reverse-consumer regressions cover existing dashboard/domain selectors and prove reports do not
  change application, loan, financial, compliance, or audit rows.
- Query-count assertions prevent per-row/N+1 access on representative pages.

## Visual Acceptance Criteria
None.

## Evidence Required
RED/GREEN evidence, focused selector/API/permission output, six example responses (including one
empty and one forbidden case), reconciliation counts, query-count evidence, and the full gate.

## Non-Goals
Export jobs/files, report frontend wiring, audit explorer, dashboard redesign, scheduling, saved
report views, or speculative materialized-view optimisation.

## Risk Level
Medium

## Acceptance Criteria
- All six section-40 report endpoints return reconciled, filtered, paginated system data through
  report-specific selectors.
- Role/object restrictions are enforced by the backend and covered by negative tests.
- Report reads are deterministic and read-only, with bounded queries and no new report storage.
- No export jobs, export files, frontend wiring, audit explorer, dashboard redesign, scheduling,
  or saved report views are included.

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
