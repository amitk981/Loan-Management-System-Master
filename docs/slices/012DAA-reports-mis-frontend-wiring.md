# Slice 012DAA: Reports and MIS Frontend Wiring

## Status
Not Started

## Origin
Oversized slice: `012DA`

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Goal
Wire the read-only Reports and MIS Center (S69) to the report APIs built in 012A, including
source-defined filters, sorting, pagination, role scope, reconciliation, and truthful UI states.

## User Value
CFO, auditors, and management can read real, scoped operational and MIS reports without relying
on prototype fixtures.

## Depends On
- 012D2

## Runtime Capabilities

- `localhost-e2e-server`

## Trusted Browser Acceptance

- Spec: `e2e/reports-exports-audit-explorer.e2e.spec.ts`
- Screenshot: `report-results.png`

## Source References
- docs/source/screen-spec.md screen S69 (Reports and MIS Center)
- docs/source/api-contracts.md sections 40 (reporting) and 8 (pagination/filtering for large
  result sets)
- docs/source/information-architecture.md (reports navigation)
- `docs/working/digests/epic-012-reports-exports-hardening-uat.md` §012DAA

## Prototype Reference
- sfpcl-lms/src/pages/reports/ReportsMIS.tsx

## Concrete Requirements
1. Wire `ReportsMIS.tsx` report reads to the 012A report APIs with filterable, sortable,
   paginated views per api-contracts §8.
2. Match report filters to the source-defined roles and parameters, preserve backend authority,
   and round-trip the active filter state without inventing client-side business rules.
3. Reconcile displayed report rows and totals to the seeded system-of-record fixtures.
4. Use existing page and status patterns for loading, empty, error, and unauthorized report
   states. Keep export actions at their existing seam for 012DAB; do not fake export success.

## Owned Mock Removals
This slice removes mock-backed report result reads from `src/pages/reports/ReportsMIS.tsx`.
012DAB owns the file's final `src/data/mockData.ts` import and inline business-fixture removal
after it wires the remaining export actions.

## Test Cases
- Report filters round-trip and results match seeded fixtures.
- Sorting and pagination use the backend contract and preserve active filters.
- Loading, empty, error, and unauthorized report states render truthfully without data leakage.

## Out of Scope
Export job actions and downloads (012DAB), Audit Log Explorer and auditor observations (012DAC),
new report definitions beyond source docs, operational dashboard hardening (012E), and the
security regression suite (012F).

## Evidence Required
Saved RED/GREEN frontend request, filter, sorting, pagination, and status tests; report
reconciliation and role-denial evidence; `report-results.png` from two passing runs of the trusted
browser spec; focused 012A regressions and full configured gates.

## Predicted Diff
Approximately 1,050 changed lines, leaving about 950 lines below the configured 2,000-line limit.

## Risk Level
Medium

## Acceptance Criteria
- S69 report reads run on backend data end to end with source-defined filters, sorting,
  pagination, reconciliation, and permissions.
- Mock-backed report result reads are removed from `ReportsMIS.tsx`; no export or audit scope is
  absorbed.
- Focused regressions, configured gates, and the two-run report screenshot contract pass.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Permissions tested
- [ ] Report reconciliation evidence saved
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Substantive unresolved risk or decision recorded only if needed
- [ ] Commit created only after passing gates
