# Slice 011PD: Compliance Tracker Staff Frontend Wiring

## Status
Not Started

## Origin
Oversized slice: `011P`

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance
Epic file: `docs/epics/011-default-recovery-closure-compliance.md`

## Goal
Wire the S62-S67 Compliance Dashboard to backend-owned control, statutory, KYC, annual-review, and
stamp-duty tracker projections.

## User Value
Compliance staff review real statutory and KYC obligations, while auditors retain an accurate
read-only view and no tracker depends on mock data.

## Depends On
- 011PC

## Runtime Capabilities

- `localhost-e2e-server`

## Trusted Browser Acceptance

- Spec: `e2e/default-closure-compliance-staff.e2e.spec.ts`
- Screenshot: `compliance-trackers.png`

## Source References
- docs/source/screen-spec.md screens S62-S67
- docs/source/api-contracts.md section 37 (compliance)
- docs/source/functional-spec.md compliance business rules
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011P

## Prototype Reference
- sfpcl-lms/src/pages/compliance/ComplianceDashboard.tsx

## Concrete Requirements
1. Wire `ComplianceDashboard.tsx` control tracker from 011K.
2. Wire Section 186 and NBFC test trackers from 011L.
3. Wire KYC/re-KYC tracker from 011M.
4. Wire money-lending annual review and the stamp duty register view backed by 008D data.
5. Expose read/review actions only as projected for the current role; auditor access remains
   read-only.
6. Loading, empty, error, unauthorized, validation, blocked, and success states throughout;
   existing patterns only.
7. Extend the shared Epic 011 staff API seam only for S62-S67 reads/review actions and cover its
   request, action, and canonical-refetch contracts with focused tests.

## Owned Mock Removals
This slice is the final owner of `src/pages/compliance/ComplianceDashboard.tsx`: after 011PD, the
file must not import `src/data/mockData.ts` or retain inline compliance tracker business fixtures.

## Test Cases
- Compliance tracker values match seeded control, Section 186, NBFC, KYC/re-KYC, money-lending, and
  stamp-duty fixtures.
- Auditor role sees read-only state with no review mutations.

## Out of Scope
Default/Recovery Hub (011PA/011PB); Loan Closure Hub (011PC); staff grievance and Audit Archive Hub
(011PE); member portal closure/NOC and support views (MP20 in 011x portal scope, 011NA); auditor
read-only views outside this dashboard (011O done); report exports (012B/012C).

## Evidence Required
Saved RED/GREEN frontend request/action/render output for the Compliance Dashboard owner; scoped
role/action/blocker and compliance mock-removal matrix rows; `compliance-trackers.png` from two
passing trusted-browser contract runs; focused Epic 011 reverse-consumer tests and configured full
gates.

## Risk Level
Medium

## Predicted Diff
Approximately 750-1,050 changed lines across the compliance page, focused request/action/render
tests, shared API additions, and scoped trusted-browser scenario. This leaves at least 950 lines of
margin under the configured 2,000-line limit.

## Acceptance Criteria
- S62-S67 run on backend data with role-correct review actions and read-only auditor behavior.
- Tracker values match seeded backend fixtures.
- No mock-data reads or inline business fixtures remain in `ComplianceDashboard.tsx`.
- All gates pass and `compliance-trackers.png` is saved from both contract runs.

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
