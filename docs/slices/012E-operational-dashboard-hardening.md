# Slice 012E: Operational Dashboard Hardening

## Status
Not Started

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Goal
Complete role-scoped dashboard APIs and wire the staff Dashboard to real, bounded summaries whose
counts and links reconcile to existing domain selectors for each operational role.

## User Value
Credit, compliance, finance, treasury, accounts, and CS users begin with an accurate view of their
pending work and risk indicators instead of static or partially populated dashboard data.

## Depends On
- 012D

## Source References
- `docs/source/api-contracts.md` sections 43-44
- `docs/source/information-architecture.md` section 9.1
- `docs/source/technical-architecture.md` sections 21.1-21.2 and 24
- `docs/source/deployment-ops.md` section 42.2
- `docs/source/test-plan.md` sections 18.2 and 24.1-24.2 (`PERF-002`)
- `docs/source/screen-spec.md` section 12
- `docs/working/digests/epic-012-reports-exports-hardening-uat.md` section 012E

## Prototype Reference
- sfpcl-lms/src/pages/reports/ReportsMIS.tsx
- sfpcl-lms/src/pages/registers/RegistersHub.tsx
- sfpcl-lms/src/pages/Dashboard.tsx

## Screens Involved
Staff Dashboard (`sfpcl-lms/src/pages/Dashboard.tsx`) for Credit, Compliance, CFO, Treasury,
Accounts, and CS role contexts.

## Frontend Scope
- Wire Dashboard to the authenticated role-based API; the caller cannot select a different role.
- Render stable cards/counts/links using existing components and patterns only. Card links must
  preserve the backend's scoped filter destination.
- Add loading, empty, partial/failed, forbidden, and refresh states without fake counts or
  `mockData.ts` fallback. Preserve `tasks[]` compatibility; real task population belongs to
  012EA/012EB.

## Backend/API Scope
- Complete `GET /api/v1/dashboard/`, `/dashboard/sanction-committee/`,
  `/dashboard/compliance/`, and `/dashboard/treasury/` per `api-contracts.md` 43.
- Derive role context from the authenticated user and build cards from existing domain/report
  selectors. Stable `code`, `label`, `count`, and scoped `link` values must reconcile to the
  linked list/report with the same filters.
- Cover the source role cards for Credit Manager, Compliance, CFO, Treasury, Accounts, and CS;
  return only cards authorised for the effective role/team/object scope.
- Batch/aggregate queries to avoid one query per card/row; instrument representative query count
  and response time against the dashboard <3-second target.

## Database/Model Impact
None. Dashboards are read models over canonical records, not persisted duplicate counters.

## API Contracts
Preserve section-43 shapes and document the stable card catalogue/role mapping. Do not extend the
task resource contract owned by 012EA.

## Permissions
Backend derives role/team scope and denies dedicated dashboards to unauthorised callers. Hidden
frontend cards are not a security boundary; target links remain independently permission-checked.

## Audit Requirements
Dashboard reads create no business workflow events and must not log card/result data containing
sensitive details. Preserve ordinary request/access logging policy.

## Validation Rules
- Every card count reconciles to the canonical target selector with the card link filters.
- No caller-controlled role override, cross-team totals, fake fallback counts, or unbounded rows.
- Dashboard remains read-only; tasks and cards cannot mutate source records.

## Test Cases
- Service/API tests for every supported role, card code/count/link reconciliation, no-role and
  multi-role resolution, 401/403, and cross-team/object isolation.
- Frontend tests for API data and loading/empty/error/forbidden/refresh states, card navigation,
  and absence of mock fallback.
- Reverse-consumer tests cover domain/report selectors and target-list filters, navigation
  permissions, existing dashboard consumers, and empty `tasks[]` until 012EA.
- Query-count and representative performance test covers the 50-user dashboard load risk without
  asserting an unreliable wall-clock threshold in unit CI.

## Visual Acceptance Criteria
Match the existing prototype patterns and include loading, empty, error, unauthorized, validation, and success states where relevant.

## Evidence Required
RED/GREEN; role/card reconciliation matrix; API and frontend test output; query-count/performance
evidence; screenshots for populated, empty, error, and forbidden states; full gates.

## Non-Goals
Task engine/inbox work, new dashboard styling/components, reports/audit UI, persisted counters, or
DevOps/security/integration monitoring dashboards.

## Risk Level
Medium

## Acceptance Criteria
- All section-43 dashboards return role-scoped, reconciled cards through bounded selectors and
  Dashboard renders them without mock fallback.
- Card links reach independently authorised lists/reports with matching filters and counts.
- Role leakage, caller role override, N+1 query growth, and mutation are regression-tested.
- Task-engine/inbox work, new dashboard styling, reports UI, and deployment monitoring dashboards
  remain out of scope.

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
