# Slice 012A2: Finance and Servicing Report Catalogue

## Status
Complete

## Runtime Capabilities
- `none`

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Origin
Owner-chat source-coverage audit on 2026-07-19 found that 012A/012B covered six report endpoints while
R8-AC-001 requires the complete critical report catalogue.

## Goal
Extend the 012A report registry with the missing credit, finance, and servicing reports using the
canonical selectors already delivered by their owning epics.

## User Value
Credit, Accounts, Treasury, and CFO can reconcile operational and financial work from one governed
report catalogue instead of exporting ad-hoc model queries.

## Depends On
- 012A

## Source References
- `docs/source/implementation-roadmap.md` section 17.3 and R8-AC-001
- `docs/source/screen-spec.md` S69 report centre and the owning register/report screens
- `docs/source/api-contracts.md` section 40 and standard pagination/filtering conventions
- `docs/source/auth-permissions.md` report/register read permissions and object scope
- `docs/source/security-privacy.md` report minimisation and masking rules
- `docs/working/digests/epic-012-reports-exports-hardening-uat.md`

## Prototype Reference
- `sfpcl-lms/src/pages/reports/ReportsMIS.tsx`
- `sfpcl-lms/src/pages/registers/RegistersHub.tsx`

## Screens Involved
None in this slice; 012DA owns frontend wiring.

## Frontend Scope
None.

## Backend/API Scope
- Register source-backed selectors/codes for Credit Sanction, Exception, Security Custody, SAP
  Pending, Disbursement, Repayment, Interest Invoice, Interest Accrual, and CFO Quarterly MIS
  reports. The full Disbursement Report includes amount, UTR/reference, status, and date and is not
  conflated with 012A's pending-disbursement API.
- Reuse the owning aggregate/register selectors; do not duplicate workflow, financial, or approval
  calculations inside reporting.
- Provide documented filters, deterministic ordering, pagination, totals where source-backed, and
  permission/object scope for every code.
- Keep export generation in 012B/012C and UI work in 012DA.

## Database/Model Impact
None expected. Add an index only with measured query-plan evidence and a non-destructive migration.

## API Contracts
Extend the section-40 report registry in `docs/working/API_CONTRACTS.md` with stable codes, filters,
fields, totals, permissions, and source-owner reconciliation notes.

## Permissions
Map each report to its existing register/resource read permission plus object/team scope. Unknown
or unresolved mappings default-deny rather than falling back to broad report access.

## Audit Requirements
Routine reads follow established access policy; no report row values are copied into audit payloads.

## Validation Rules
- Every row and total reconciles to persisted source-owner truth for the same filters/as-of time.
- Dates, money, pagination, ordering, masking, and empty/unauthorised behavior follow section 40.
- Query counts remain bounded on representative fixtures.

## Test Cases
- RED then GREEN for every report code: seeded source reconciliation, filters, stable ordering,
  pagination, totals, empty result, invalid filter, 401/403, and cross-scope denial.
- Reverse-consumer tests prove report selectors do not mutate or reimplement owner calculations.

## Visual Acceptance Criteria
Not applicable (backend only).

## Evidence Required
Saved RED/GREEN output; code-to-source/permission matrix; seeded row/total reconciliation; filter and
scope examples; query-count evidence; reverse-consumer and full gates.

## Risk Level
Medium

## Acceptance Criteria
- All nine named finance/servicing catalogue reports are registered, reconciled, scoped, and
  export-ready; Loan Request/Loan Register ownership stays in 012A without duplication.
- No duplicate business calculation or broad permission grant is introduced.
- Required focused, reverse-consumer, and full gates pass.

## Done Checklist
- [ ] Execution plan written
- [ ] TDD RED/GREEN evidence saved
- [ ] Report codes/selectors/contracts implemented
- [ ] Reconciliation, permissions, masking, and query bounds tested
- [ ] Full gates passed
- [ ] Risk and review evidence completed
- [ ] Commit delegated to the orchestrator after gates
