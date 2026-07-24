# Slice 012DAB: Report and Register Export Frontend Wiring

## Status
Not Started

## Origin
Oversized slice: `012DA`

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Goal
Wire report and register export actions to the 012B/012C export job APIs, including permission
denial, masking, asynchronous status, audited download, and final owned mock removal.

## User Value
Authorized staff can run and download permission-checked masked exports, while unauthorized or
failed work is surfaced honestly.

## Depends On
- 012DAA

## Runtime Capabilities

- `localhost-e2e-server`

## Trusted Browser Acceptance

- Spec: `e2e/reports-exports-audit-explorer.e2e.spec.ts`
- Screenshot: `export-job-status.png`
- Screenshot: `masked-export.png`

## Source References
- docs/source/screen-spec.md screen S69 (Reports and MIS Center)
- docs/source/api-contracts.md section 40 (reporting and export jobs)
- docs/source/security-privacy.md (export masking rules)
- docs/source/information-architecture.md (reports navigation)
- `docs/working/digests/epic-012-reports-exports-hardening-uat.md` §012DAB

## Prototype Reference
- sfpcl-lms/src/pages/reports/ReportsMIS.tsx
- sfpcl-lms/src/pages/registers/RegistersHub.tsx (export actions)

## Concrete Requirements
1. Wire export actions in `RegistersHub.tsx` and `ReportsMIS.tsx` to the 012B/012C export job APIs:
   start a job, preserve the backend job identity, poll or refresh status, and download only when
   the audited backend contract reports the file ready.
2. Render queued, running, failed, and ready states with existing status patterns. Cover loading,
   empty, error, unauthorized, validation, and success states without client-side success claims.
3. Render sensitive columns masked for non-authorized roles and surface backend rejection for
   unauthorized export attempts without leaking restricted values.
4. Preserve the separate report-read permission and export permission boundary; the UI may hide
   unavailable actions, but backend denials remain authoritative and visible.

## Owned Mock Removals
This slice is the final owner of these files' mock surface. After it, neither file may import
`src/data/mockData.ts` or retain inline business fixtures:
- `src/pages/reports/ReportsMIS.tsx`
- `src/pages/registers/RegistersHub.tsx` (S23/S25 views were wired by 007J; remaining register
  views and the final import removal happen here)

## Test Cases
- Export by a non-permitted role is rejected and surfaced without restricted data.
- A permitted export progresses through the backend job states and shows masked sensitive columns.
- A ready job downloads only through the audited backend download path; failed and stale states
  never expose a download success.
- Report and register loading, empty, error, unauthorized, validation, and success states remain
  truthful.

## Out of Scope
Report result wiring (012DAA), Audit Log Explorer and auditor observations (012DAC), new report
definitions beyond source docs, operational dashboard hardening (012E), and the security
regression suite (012F).

## Evidence Required
Saved RED/GREEN frontend export request, status, masking, permission-denial, and download tests;
export masking, backend rejection, audited-download, and state-transition evidence;
`export-job-status.png` and `masked-export.png` from two passing runs of the trusted browser spec;
focused 012B/012C regressions and full configured gates.

## Predicted Diff
Approximately 1,250 changed lines, leaving about 750 lines below the configured 2,000-line limit.

## Risk Level
Medium

## Acceptance Criteria
- Report and register export flows run on 012B/012C backend data end to end with masking,
  permissions, job status, and audited downloads enforced.
- No mock-data reads or inline business fixtures remain in `ReportsMIS.tsx` or `RegistersHub.tsx`.
- Focused regressions, configured gates, and both two-run export screenshot contracts pass.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Export masking and download evidence saved
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Substantive unresolved risk or decision recorded only if needed
- [ ] Commit created only after passing gates
