# Slice 011PE: Grievance and Audit Archive Staff Frontend Wiring

## Status
Not Started

## Origin
Oversized slice: `011P`

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance
Epic file: `docs/epics/011-default-recovery-closure-compliance.md`

## Goal
Wire the S68 staff Grievance Register and the read-only Audit Archive Hub, then run the terminal
combined browser acceptance for every screen inherited from oversized slice 011P.

## User Value
Compliance staff resolve real grievances with governed reasons, auditors download real archive
records through an audited read-only path, and the complete default-to-compliance staff surface is
validated without mock data.

## Depends On
- 011PD

## Runtime Capabilities

- `localhost-e2e-server`

## Trusted Browser Acceptance

- Spec: `e2e/default-closure-compliance-staff.e2e.spec.ts`
- Screenshot: `default-case-workbench.png`
- Screenshot: `recovery-approval-decision.png`
- Screenshot: `closure-readiness-blockers.png`
- Screenshot: `compliance-trackers.png`
- Screenshot: `grievance-resolution.png`

## Source References
- docs/source/screen-spec.md screen S68
- docs/source/api-contracts.md sections 36 (closure/archive) and 38 (grievance)
- docs/source/functional-spec.md closure/compliance/grievance business rules
- docs/source/user-flows.md (closure flow)
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011P

## Prototype Reference
- sfpcl-lms/src/pages/compliance/GrievancesHub.tsx
- sfpcl-lms/src/pages/compliance/AuditArchiveHub.tsx

## Concrete Requirements
1. Wire staff `GrievancesHub.tsx` to 011N list/resolve APIs; resolution requires status and reason.
2. Wire `AuditArchiveHub.tsx` to archive records from 011J as a read-only surface with audited
   downloads and no mutation controls.
3. Loading, empty, error, unauthorized, validation, blocked, and success states throughout;
   existing patterns only.
4. Extend the shared Epic 011 staff API seam only for grievance and audit-archive reads/actions and
   cover request, action, download, and canonical-refetch contracts with focused tests.
5. Complete the shared trusted-browser spec and run the entire S53-S68 contract twice, preserving
   all five original screenshots.

## Owned Mock Removals
This slice is the final owner of:
- `src/pages/compliance/GrievancesHub.tsx`
- `src/pages/compliance/AuditArchiveHub.tsx`

After 011PE, neither file may import `src/data/mockData.ts` or retain inline grievance/archive
business fixtures. Together with 011PA-011PD, none of the five files originally owned by 011P may
retain mock-data reads or inline business fixtures.

## Test Cases
- Grievance resolve without reason is rejected and surfaced cleanly.
- Grievance resolution submits the server-projected status/action and refetches canonical state.
- Audit archive is read-only and downloads use the governed audited endpoint.
- The complete S53-S68 trusted-browser contract passes twice with the original five screenshots.

## Out of Scope
Member portal closure/NOC and support views (MP20 in 011x portal scope, 011NA); auditor read-only
views outside these inherited staff surfaces (011O done); report exports (012B/012C).

## Evidence Required
Saved RED/GREEN frontend request/action/render output for both the Grievance Register and Audit
Archive Hub owners; completed role/action/blocker and five-owner mock-removal matrices; all five
trusted-browser screenshots from two passing complete contract runs; focused Epic 011
reverse-consumer tests and configured full gates.

## Risk Level
Medium

## Predicted Diff
Approximately 900-1,300 changed lines across the two bounded pages, focused
request/action/render/download tests, shared API additions, and terminal trusted-browser completion.
This leaves at least 700 lines of margin under the configured 2,000-line limit.

## Acceptance Criteria
- S68 staff grievance and audit-archive screens run on backend data with role-correct actions.
- Grievance resolution requires status and reason; archive access remains read-only and audited.
- No mock-data reads or inline business fixtures remain in any of the five original 011P owners.
- The complete S53-S68 staff contract passes twice and saves
  `default-case-workbench.png`, `recovery-approval-decision.png`,
  `closure-readiness-blockers.png`, `compliance-trackers.png`, and
  `grievance-resolution.png`.
- All focused reverse-consumer and configured full gates pass.

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
- [ ] Ralph owns mechanical bookkeeping; record only substantive unresolved risks/decisions in `review-packet.md` and `HANDOFF` if needed
- [ ] Commit created only after passing gates
