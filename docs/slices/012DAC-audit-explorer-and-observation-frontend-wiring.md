# Slice 012DAC: Audit Explorer and Observation Frontend Wiring

## Status
Not Started

## Origin
Oversized slice: `012DA`

## Parent Epic
Epic 012: Reports, Exports, Hardening, Regression, and UAT Readiness
Epic file: `docs/epics/012-reports-exports-hardening-uat.md`

## Goal
Wire the read-only Audit Log Explorer (S74) and the separately scoped auditor observation workflow
to the 012D/012D2 APIs with pagination, filtering, restricted-field protection, and immutable
observation behaviour.

## User Value
Auditors can explore the real audit trail and record governed observations against scoped
evidence without turning immutable audit records into editable data.

## Depends On
- 012DAB

## Runtime Capabilities

- `localhost-e2e-server`

## Trusted Browser Acceptance

- Spec: `e2e/reports-exports-audit-explorer.e2e.spec.ts`
- Screenshot: `audit-explorer.png`
- Screenshot: `audit-observation-recorded.png`

## Source References
- docs/source/screen-spec.md screen S74 (Audit Log Explorer)
- docs/source/api-contracts.md sections 42 (audit and workflow APIs) and 8
  (pagination/filtering for large result sets)
- docs/source/security-privacy.md (restricted audit fields)
- docs/source/information-architecture.md (audit navigation)
- `docs/working/digests/epic-012-reports-exports-hardening-uat.md` §012DAC

## Prototype Reference
- sfpcl-lms/src/pages/compliance/AuditArchiveHub.tsx (audit explorer entry, if routed there)

## Concrete Requirements
1. Wire the Audit Log Explorer (S74) to the 012D APIs with entity, action, actor, and date filters,
   deterministic pagination, and backend-authoritative scope.
2. Keep audit results strictly read-only: issue no audit-log write calls, render no edit affordance,
   and never render restricted fields or raw sensitive values.
3. For an explicitly scoped sampled result, expose the separate 012D2 auditor-only observation
   form and observation list/detail. It creates immutable observation records and never turns the
   audit-log row into an editable record.
4. Use existing patterns for loading, empty, error, unauthorized, validation, and success states
   across explorer filters, result detail, observation creation, and observation revisit.
5. Preserve the complete trusted browser spec accumulated by 012DAA/012DAB and prove all five
   original screenshots through two passing runs before terminal completion.

## Owned Mock Removals
Remove any audit-explorer or observation business fixtures introduced by the prototype seam.
Together with completed 012DAA/012DAB ownership, terminal completion leaves no mock-data reads in
the original 012DA reports, exports, or audit screens.

## Test Cases
- Audit explorer filters by entity, action, actor, and date with deterministic pagination.
- Audit explorer cannot mutate anything (no audit-log write calls) and never renders restricted
  fields.
- A scoped Internal Auditor can record and revisit an M14-FR-012 observation.
- Other roles, foreign evidence, lifecycle fields, and attempted edits are rejected and surfaced
  without data leakage.
- Loading, empty, error, unauthorized, validation, and success states remain truthful.

## Out of Scope
Report result wiring (012DAA), export workflow wiring (012DAB), new report definitions beyond
source docs, operational dashboard hardening (012E), and the security regression suite (012F).

## Evidence Required
Saved RED/GREEN frontend audit request, filter, pagination, read-only, restricted-field,
observation-create, and observation-revisit tests; read-only explorer and immutable observation
permission/denial evidence; `audit-explorer.png` and `audit-observation-recorded.png` from two
passing runs of the trusted browser spec; the terminal two-run browser evidence must also retain
`report-results.png`, `export-job-status.png`, and `masked-export.png`; focused 012D/012D2
regressions and full configured gates.

## Predicted Diff
Approximately 1,350 changed lines, leaving about 650 lines below the configured 2,000-line limit.

## Risk Level
Medium

## Acceptance Criteria
- S74 and the separate auditor observation flow run on 012D/012D2 backend data end to end with
  filters, pagination, permissions, immutability, and restricted-field protection enforced.
- No mock-data reads remain in the original 012DA reports, exports, or audit screens.
- All original 012DA requirements and acceptance contracts are complete across 012DAA-012DAC.
- Focused regressions, configured gates, and all five original screenshots from two passing
  trusted-browser runs pass.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Permissions tested
- [ ] Audit immutability and restricted fields tested
- [ ] Observation authorization and immutability tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Substantive unresolved risk or decision recorded only if needed
- [ ] Commit created only after passing gates
