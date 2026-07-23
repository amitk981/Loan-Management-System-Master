# Slice 011PB: Recovery Decision Staff Frontend Wiring

## Status
Not Started

## Origin
Oversized slice: `011P`

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance
Epic file: `docs/epics/011-default-recovery-closure-compliance.md`

## Goal
Complete the S56 recovery-decision action in the Default/Recovery Hub and make the already-delivered
S57 execution control available only from an approved, executable backend decision.

## User Value
Authorised Credit and CFO staff can decide recovery from frozen evidence, while conflicted,
rejected, foreign, or incomplete approval evidence remains visibly and technically blocked.

## Depends On
- 011PA

## Runtime Capabilities

- `localhost-e2e-server`

## Trusted Browser Acceptance

- Spec: `e2e/default-closure-compliance-staff.e2e.spec.ts`
- Screenshot: `recovery-approval-decision.png`

## Source References
- docs/source/screen-spec.md screens S56-S57 and section 9.9 (default rules)
- docs/source/api-contracts.md section 35 (default/recovery)
- docs/source/functional-spec.md default/recovery business rules
- docs/source/user-flows.md (default flow)
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011P

## Prototype Reference
- sfpcl-lms/src/pages/defaults/DefaultRecoveryHub.tsx

## Concrete Requirements
1. Wire the complete S56 recovery-decision action from 011E in `DefaultRecoveryHub.tsx`.
2. Show the frozen non-payment note, required approval/authority/conflict evidence, source-permitted
   decision, mandatory reason, terminal outcome, and exact blockers.
3. Make the already-delivered S57 execution control from 011F available only when the backend
   projects an approved executable decision. The browser cannot supply approval or authority truth.
4. Pending, rejected, conflicted, foreign, or otherwise ineligible approval evidence must remain
   visibly blocked and cannot unlock S57 through a handcrafted request.
5. Loading, empty, error, unauthorized, validation, blocked, and success states throughout;
   existing patterns only.
6. Extend the shared Epic 011 staff API seam only for the S56 reads/actions owned here and cover
   request, action, and canonical-refetch contracts with focused tests.

## Owned Mock Removals
This slice is the final owner of `src/pages/defaults/DefaultRecoveryHub.tsx`: after 011PB, the file
must not import `src/data/mockData.ts` or retain inline default/recovery business fixtures.

## Test Cases
- Recovery execution actions remain hidden/disabled without an approved decision.
- S56 permits only source-authorised decision actions; pending/rejected/conflicted/foreign approval
  evidence is visibly blocked and cannot unlock S57 through a handcrafted request.
- A mandatory reason is enforced and a terminal decision refetches and renders canonical backend
  state.

## Out of Scope
S53-S55 read wiring (011PA); Loan Closure Hub (011PC); Compliance Dashboard (011PD); staff grievance
and Audit Archive Hub (011PE); member portal closure/NOC and support views (MP20 in 011x portal
scope, 011NA); auditor read-only views (011O done); report exports (012B/012C).

## Evidence Required
Saved RED/GREEN frontend request/action/render output for the S56/S57 owner; scoped
role/action/blocker and final Default/Recovery Hub mock-removal matrix rows;
`recovery-approval-decision.png` from two passing trusted-browser contract runs; focused Epic 011
reverse-consumer tests and configured full gates.

## Risk Level
Medium

## Predicted Diff
Approximately 800-1,150 changed lines across the recovery-decision page seam, focused
request/action/render tests, shared API additions, and scoped trusted-browser scenario. This leaves
at least 850 lines of margin under the configured 2,000-line limit.

## Acceptance Criteria
- S56 runs on backend data with role-correct, blocker-driven decision actions and mandatory reason.
- S57 cannot become available without an approved executable server-owned decision.
- No mock-data reads or inline business fixtures remain in `DefaultRecoveryHub.tsx`.
- All gates pass and `recovery-approval-decision.png` is saved from both contract runs.

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
