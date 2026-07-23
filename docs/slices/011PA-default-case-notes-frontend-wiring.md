# Slice 011PA: Default Case and Notes Staff Frontend Wiring

## Status
Not Started

## Origin
Oversized slice: `011P`

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance
Epic file: `docs/epics/011-default-recovery-closure-compliance.md`

## Goal
Wire the S53-S55 read side of the Default/Recovery Hub to the backend built in 011A-011D: default
case list/detail, grace and extension tracking, and frozen non-payment notes.

## User Value
Credit staff see real delinquency, grace, extension, and non-payment evidence without mock data,
while recovery actions remain unavailable until the governed decision wiring arrives in 011PB.

## Depends On
- 011O

## Runtime Capabilities

- `localhost-e2e-server`

## Trusted Browser Acceptance

- Spec: `e2e/default-closure-compliance-staff.e2e.spec.ts`
- Screenshot: `default-case-workbench.png`

## Source References
- docs/source/screen-spec.md screens S53-S55 and section 9.9 (default rules)
- docs/source/api-contracts.md section 35 (default/recovery)
- docs/source/functional-spec.md default business rules
- docs/source/user-flows.md (default flow)
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011P

## Prototype Reference
- sfpcl-lms/src/pages/defaults/DefaultRecoveryHub.tsx

## Concrete Requirements
1. Wire `DefaultRecoveryHub.tsx` default case list/detail to 011A backend projections.
2. Render grace tracking from 011B and extension notes from 011C.
3. Render the frozen non-payment note from 011D; the browser must not manufacture or amend frozen
   evidence.
4. Keep recovery-decision and execution actions hidden or disabled until 011PB supplies the
   server-owned S56/S57 availability contract.
5. Loading, empty, error, unauthorized, and blocked states throughout; existing patterns only.
6. Extend the shared Epic 011 staff API seam only for the S53-S55 reads owned here and cover its
   request contracts with focused tests.

## Owned Mock Removals
Remove every inline or `src/data/mockData.ts` business fixture for S53-S55 from
`src/pages/defaults/DefaultRecoveryHub.tsx`. Presentation-only tab/filter definitions may remain.
011PB is the final owner of any recovery-decision/execution fixture surface left in this file.

## Test Cases
- Default case list/detail, grace/extension state, and frozen non-payment note render from seeded
  backend fixtures.
- Loading, empty, error, unauthorized, and absent-note/blocked projections render truthfully.
- Recovery decision/execution actions remain unavailable before an approved server-owned decision
  is wired.

## Out of Scope
S56 recovery-decision action and S57 execution availability (011PB); Loan Closure Hub (011PC);
Compliance Dashboard (011PD); staff grievance and Audit Archive Hub (011PE); member portal
closure/NOC and support views (MP20 in 011x portal scope, 011NA); auditor read-only views (011O
done); report exports (012B/012C).

## Evidence Required
Saved RED/GREEN frontend request/render output for the Default/Recovery Hub S53-S55 owner; scoped
role/action/blocker and mock-removal matrix rows; `default-case-workbench.png` from two passing
trusted-browser contract runs; focused Epic 011 reverse-consumer tests and configured full gates.

## Risk Level
Medium

## Predicted Diff
Approximately 750-1,050 changed lines across the default page, focused request/render tests, the
shared API seam, and the scoped trusted-browser scenario. This leaves at least 950 lines of margin
under the configured 2,000-line limit.

## Acceptance Criteria
- S53-S55 staff views run on backend data with truthful frozen evidence and blocker states.
- No S53-S55 mock-data reads or inline business fixtures remain.
- Recovery actions cannot become available from browser-supplied truth.
- All gates pass and `default-case-workbench.png` is saved from both contract runs.

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
