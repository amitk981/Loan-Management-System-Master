# Slice 011P: Default, Closure, Compliance, and Grievance Staff Frontend Wiring

## Status
Not Started

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance
Epic file: `docs/epics/011-default-recovery-closure-compliance.md`

## Goal
Wire the remaining Epic 011 staff screens to the backend built in 011A-011N: Default/Recovery Hub (S53 default case detail, S54 grace/extension, S55 non-payment note — recovery execution UI arrived in 011F), Loan Closure Hub (S58 closure, S59 NOC, S60 security return, S61 archive), Compliance Dashboard (S62 dashboard, S63 Section 186, S64 NBFC test, S65 KYC/re-KYC tracker, S67 money-lending review), staff Grievance Register (S68), and the Audit Archive Hub.

## User Value
Credit, CFO, CS, and Compliance manage real delinquency, closure, and statutory compliance work — blockers and approval states come from the backend, and nothing depends on mock data.

## Depends On
- 011O

## Source References
- docs/source/screen-spec.md screens S53-S55, S58-S68 and sections 9.9 (default rules), 9.10 (closure rules)
- docs/source/api-contracts.md sections 35 (default/recovery), 36 (closure), 37 (compliance), 38 (grievance)
- docs/source/functional-spec.md default/closure/compliance business rules
- docs/source/user-flows.md (default and closure flows)

## Prototype Reference
- sfpcl-lms/src/pages/defaults/DefaultRecoveryHub.tsx
- sfpcl-lms/src/pages/closure/LoanClosureHub.tsx
- sfpcl-lms/src/pages/compliance/ComplianceDashboard.tsx
- sfpcl-lms/src/pages/compliance/GrievancesHub.tsx
- sfpcl-lms/src/pages/compliance/AuditArchiveHub.tsx

## Concrete Requirements
1. Wire `DefaultRecoveryHub.tsx` remainder: default case list/detail (011A), grace tracking (011B), extension notes (011C), non-payment notes (011D), recovery decision state (011E) — approval blockers visible before any execution action (011F UI already exists).
2. Wire `LoanClosureHub.tsx`: closure readiness with named blockers (011G), NOC issuance state (011H), security return/unpledge tracking (011I), archive record state (011J).
3. Wire `ComplianceDashboard.tsx`: control tracker (011K), Section 186 and NBFC test trackers (011L), KYC/re-KYC tracker (011M), money-lending annual review, stamp duty register view (008D data) — read/review actions per role.
4. Wire staff `GrievancesHub.tsx` to 011N list/resolve APIs; resolution requires status and reason.
5. Wire `AuditArchiveHub.tsx` to archive records (011J) — read-only with audited downloads.
6. Loading, empty, error, unauthorized, and blocked states throughout; existing patterns only.

## Owned Mock Removals
This slice is the final owner of these files' mock surface — after it, none of them may import `src/data/mockData.ts` or keep inline business fixtures:
- `src/pages/compliance/ComplianceDashboard.tsx`
- `src/pages/compliance/GrievancesHub.tsx`
- `src/pages/compliance/AuditArchiveHub.tsx`
- `src/pages/defaults/DefaultRecoveryHub.tsx` and `src/pages/closure/LoanClosureHub.tsx` (whatever mock/inline fixtures remain after 011A-011O)

## Test Cases
- Closure readiness blockers render from seeded unpaid-balance/security-pending fixtures; NOC action blocked until readiness passes.
- Recovery execution actions remain hidden/disabled without an approved decision.
- Compliance tracker values match seeded fixtures; auditor role sees read-only.
- Grievance resolve without reason is rejected and surfaced cleanly.

## Out of Scope
Member portal closure/NOC and support views (MP20 in 011x portal scope, 011NA), auditor read-only views (011O done), report exports (012B/012C).

## Risk Level
Medium

## Acceptance Criteria
- All listed Epic 011 staff screens run on backend data with role-correct, blocker-driven actions.
- No mock-data reads remain in these screens.
- All gates pass; screenshots of default case, closure blockers, compliance trackers, and grievance resolution saved.

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
