# Slice 011PC: Closure, NOC, Security Return, and Archive Staff Frontend Wiring

## Status
Not Started

## Origin
Oversized slice: `011P`

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance
Epic file: `docs/epics/011-default-recovery-closure-compliance.md`

## Goal
Wire the S58-S61 Loan Closure Hub to backend-owned closure readiness, NOC issuance, security
return/unpledge, and closure archive state.

## User Value
Finance, CS, and Credit staff see named closure blockers and can progress NOC, security return, and
archive work only when the backend says the loan is ready.

## Depends On
- 011PB

## Runtime Capabilities

- `localhost-e2e-server`

## Trusted Browser Acceptance

- Spec: `e2e/default-closure-compliance-staff.e2e.spec.ts`
- Screenshot: `closure-readiness-blockers.png`

## Source References
- docs/source/screen-spec.md screens S58-S61 and section 9.10 (closure rules)
- docs/source/api-contracts.md section 36 (closure)
- docs/source/functional-spec.md closure business rules
- docs/source/user-flows.md (closure flow)
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011P

## Prototype Reference
- sfpcl-lms/src/pages/closure/LoanClosureHub.tsx

## Concrete Requirements
1. Wire `LoanClosureHub.tsx` closure readiness with named blockers from 011G.
2. Wire NOC issuance state from 011H, security return/unpledge tracking from 011I, and archive record
   state from 011J.
3. Keep NOC and downstream closure actions blocked until server-owned readiness and prerequisite
   identities pass; browser-supplied state cannot bypass the backend.
4. Loading, empty, error, unauthorized, validation, blocked, and success states throughout;
   existing patterns only.
5. Extend the shared Epic 011 staff API seam only for S58-S61 reads/actions and cover request,
   action, and canonical-refetch contracts with focused tests.

## Owned Mock Removals
This slice is the final owner of `src/pages/closure/LoanClosureHub.tsx`: after 011PC, the file must
not import `src/data/mockData.ts` or retain inline closure, NOC, security-return, or archive business
fixtures.

## Test Cases
- Closure readiness blockers render from seeded unpaid-balance/security-pending fixtures; NOC
  action is blocked until readiness passes.
- Backend-owned closure, NOC, security-return, and archive states render after each canonical
  refetch.

## Out of Scope
Default/Recovery Hub (011PA/011PB); Compliance Dashboard (011PD); staff grievance and Audit Archive
Hub (011PE); member portal closure/NOC and support views (MP20 in 011x portal scope, 011NA); auditor
read-only views (011O done); report exports (012B/012C).

## Evidence Required
Saved RED/GREEN frontend request/action/render output for the Loan Closure Hub owner; scoped
role/action/blocker and closure mock-removal matrix rows; `closure-readiness-blockers.png` from two
passing trusted-browser contract runs; focused Epic 011 reverse-consumer tests and configured full
gates.

## Risk Level
Medium

## Predicted Diff
Approximately 750-1,050 changed lines across the closure page, focused request/action/render tests,
shared API additions, and scoped trusted-browser scenario. This leaves at least 950 lines of margin
under the configured 2,000-line limit.

## Acceptance Criteria
- S58-S61 run on backend data with role-correct, named-blocker-driven actions.
- NOC remains blocked until server-owned closure readiness passes.
- No mock-data reads or inline business fixtures remain in `LoanClosureHub.tsx`.
- All gates pass and `closure-readiness-blockers.png` is saved from both contract runs.

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
