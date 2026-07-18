# Slice 012DA: Reports, Exports, and Audit Explorer Frontend Wiring

## Status
Not Started

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Goal
Wire the reporting surface to the backend built in 012A-012D: Reports and MIS Center (S69), register export actions with job status and masking behaviour (012B/012C), and the Audit Log Explorer (S74).

## User Value
CFO, auditors, and management read real reports, run permission-checked masked exports, and explore the audit trail — the oversight layer of the platform becomes fully usable.

## Depends On
- 012D

## Source References
- docs/source/screen-spec.md screens S69 (Reports and MIS Center), S74 (Audit Log Explorer)
- docs/source/api-contracts.md sections 40 (reporting), 42 (audit and workflow APIs), 8 (pagination/filtering for large result sets)
- docs/source/security-privacy.md (export masking rules)
- docs/source/information-architecture.md (reports navigation)

## Prototype Reference
- sfpcl-lms/src/pages/reports/ReportsMIS.tsx
- sfpcl-lms/src/pages/registers/RegistersHub.tsx (export actions)
- sfpcl-lms/src/pages/compliance/AuditArchiveHub.tsx (audit explorer entry, if routed there)

## Concrete Requirements
1. Wire `ReportsMIS.tsx` to the 012A report APIs: filterable, sortable, paginated report views per api-contracts §8; report filters match source-defined roles and parameters.
2. Wire export actions (RegistersHub and ReportsMIS) to the 012B/012C export job APIs: start job, poll/status display, download when ready via audited download; masked columns render masked for non-authorized roles, and unauthorized export attempts show the backend rejection.
3. Wire the Audit Log Explorer (S74) to the 012D APIs: filter by entity/action/actor/date, paginated, strictly read-only, restricted fields never rendered.
4. Long-running export states (queued/running/failed/ready) use existing status patterns; loading, empty, error, unauthorized states throughout.

## Owned Mock Removals
This slice is the final owner of these files' mock surface — after it, none of them may import `src/data/mockData.ts` or keep inline business fixtures:
- `src/pages/reports/ReportsMIS.tsx`
- `src/pages/registers/RegistersHub.tsx` (S23/S25 views wired by 007J; remaining register views and the final import removal happen here)

## Test Cases
- Report filters round-trip and results match seeded fixtures.
- Export by non-permitted role is rejected and surfaced; permitted export shows masked sensitive columns.
- Audit explorer cannot mutate anything (no write calls) and never renders restricted fields.

## Out of Scope
New report definitions beyond source docs, operational dashboard hardening (012E), security regression suite (012F).

## Risk Level
Medium

## Acceptance Criteria
- S69 and S74 plus export flows run on backend data end to end with masking and permissions enforced.
- No mock-data reads remain in reports/exports/audit screens.
- All gates pass; screenshots of a report, export status, masked export, and audit explorer saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Substantive unresolved risk or decision recorded only if needed
- [ ] Commit created only after passing gates
