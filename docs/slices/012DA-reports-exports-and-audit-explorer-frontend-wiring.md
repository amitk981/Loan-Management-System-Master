# Slice 012DA: Reports, Exports, and Audit Explorer Frontend Wiring

## Status
Superseded

## Superseded By
- 012DAA-reports-mis-frontend-wiring
- 012DAB-report-and-register-export-frontend-wiring
- 012DAC-audit-explorer-and-observation-frontend-wiring

The failed 012DA candidate measured 3,475 changed lines against the configured 2,000-line limit.
The successor chain preserves this slice's complete contract at independently green capability
seams with a predicted maximum of 1,350 changed lines.

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Goal
Wire the reporting surface to the backend built in 012A-012D: Reports and MIS Center (S69), register export actions with job status and masking behaviour (012B/012C), and the Audit Log Explorer (S74).

## User Value
CFO, auditors, and management read real reports, run permission-checked masked exports, and explore the audit trail — the oversight layer of the platform becomes fully usable.

## Depends On
- 012D2

## Runtime Capabilities

- `localhost-e2e-server`

## Trusted Browser Acceptance

- Spec: `e2e/reports-exports-audit-explorer.e2e.spec.ts`
- Screenshot: `report-results.png`
- Screenshot: `export-job-status.png`
- Screenshot: `masked-export.png`
- Screenshot: `audit-explorer.png`
- Screenshot: `audit-observation-recorded.png`

## Source References
- docs/source/screen-spec.md screens S69 (Reports and MIS Center), S74 (Audit Log Explorer)
- docs/source/api-contracts.md sections 40 (reporting), 42 (audit and workflow APIs), 8 (pagination/filtering for large result sets)
- docs/source/security-privacy.md (export masking rules)
- docs/source/information-architecture.md (reports navigation)
- `docs/working/digests/epic-012-reports-exports-hardening-uat.md` §012DA

## Prototype Reference
- sfpcl-lms/src/pages/reports/ReportsMIS.tsx
- sfpcl-lms/src/pages/registers/RegistersHub.tsx (export actions)
- sfpcl-lms/src/pages/compliance/AuditArchiveHub.tsx (audit explorer entry, if routed there)

## Concrete Requirements
1. Wire `ReportsMIS.tsx` to the 012A report APIs: filterable, sortable, paginated report views per api-contracts §8; report filters match source-defined roles and parameters.
2. Wire export actions (RegistersHub and ReportsMIS) to the 012B/012C export job APIs: start job, poll/status display, download when ready via audited download; masked columns render masked for non-authorized roles, and unauthorized export attempts show the backend rejection.
3. Wire the Audit Log Explorer (S74) to the 012D APIs: filter by entity/action/actor/date, paginated,
   strictly read-only, restricted fields never rendered. For an explicitly scoped sampled result,
   expose the separate 012D2 auditor-only observation form and observation list/detail; it creates
   immutable observation records and never turns the audit-log row into an editable record.
4. Long-running export states (queued/running/failed/ready) use existing status patterns; loading, empty, error, unauthorized states throughout.

## Owned Mock Removals
This slice is the final owner of these files' mock surface — after it, none of them may import `src/data/mockData.ts` or keep inline business fixtures:
- `src/pages/reports/ReportsMIS.tsx`
- `src/pages/registers/RegistersHub.tsx` (S23/S25 views wired by 007J; remaining register views and the final import removal happen here)

## Test Cases
- Report filters round-trip and results match seeded fixtures.
- Export by non-permitted role is rejected and surfaced; permitted export shows masked sensitive columns.
- Audit explorer cannot mutate anything (no write calls) and never renders restricted fields.
- A scoped Internal Auditor can record and revisit an M14-FR-012 observation; other roles, foreign
  evidence, lifecycle fields, and attempted edits are rejected and surfaced without data leakage.

## Out of Scope
New report definitions beyond source docs, operational dashboard hardening (012E), security regression suite (012F).

## Evidence Required
Saved RED/GREEN frontend request/filter/status/download tests; report reconciliation, export masking,
permission denial, audited-download, read-only explorer, and observation evidence; all five trusted-browser
screenshots from two passing runs; focused 012A-012D2 regressions and full gates.

## Risk Level
Medium

## Acceptance Criteria
- S69 and S74 plus export flows run on backend data end to end with masking and permissions enforced.
- No mock-data reads remain in reports/exports/audit screens.
- All gates pass; screenshots of a report, export status, masked export, audit explorer, and recorded
  audit observation saved.

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
