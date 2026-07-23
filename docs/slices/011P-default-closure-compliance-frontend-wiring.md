# Slice 011P: Default, Closure, Compliance, and Grievance Staff Frontend Wiring

## Status
Superseded

## Superseded By
- 011PA-default-case-notes-frontend-wiring
- 011PB-recovery-decision-frontend-wiring
- 011PC-closure-frontend-wiring
- 011PD-compliance-frontend-wiring
- 011PE-grievance-audit-archive-frontend-wiring

The failed 011P candidate measured 4,468 changed lines against the configured 2,000-line limit.
The successor chain preserves this slice's complete contract at independently green screen seams.

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance
Epic file: `docs/epics/011-default-recovery-closure-compliance.md`

## Goal
Wire the remaining Epic 011 staff screens to the backend built in 011A-011N: Default/Recovery Hub
(S53 default detail, S54 grace/extension, S55 non-payment note, and S56 recovery decision approval;
S57 execution UI arrived in 011F), Loan Closure Hub (S58-S61), Compliance Dashboard (S62-S67),
staff Grievance Register (S68), and the Audit Archive Hub.

## User Value
Credit, CFO, CS, and Compliance manage real delinquency, closure, and statutory compliance work — blockers and approval states come from the backend, and nothing depends on mock data.

## Depends On
- 011O

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
- docs/source/screen-spec.md screens S53-S68 and sections 9.9 (default rules), 9.10 (closure rules)
- docs/source/api-contracts.md sections 35 (default/recovery), 36 (closure), 37 (compliance), 38 (grievance)
- docs/source/functional-spec.md default/closure/compliance business rules
- docs/source/user-flows.md (default and closure flows)
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011P

## Prototype Reference
- sfpcl-lms/src/pages/defaults/DefaultRecoveryHub.tsx
- sfpcl-lms/src/pages/closure/LoanClosureHub.tsx
- sfpcl-lms/src/pages/compliance/ComplianceDashboard.tsx
- sfpcl-lms/src/pages/compliance/GrievancesHub.tsx
- sfpcl-lms/src/pages/compliance/AuditArchiveHub.tsx

## Concrete Requirements
1. Wire `DefaultRecoveryHub.tsx` remainder: default case list/detail (011A), grace tracking (011B),
   extension notes (011C), non-payment notes (011D), and the complete S56 recovery-decision action
   from 011E. Show the frozen note, required approval/authority/conflict evidence, permitted decision,
   mandatory reason, terminal outcome, and exact blockers before the already-delivered S57 execution
   control can become available. The browser cannot supply approval or authority truth.
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
- S56 permits only source-authorised decision actions; pending/rejected/conflicted/foreign approval
  evidence is visibly blocked and cannot unlock S57 through a handcrafted request.
- Compliance tracker values match seeded fixtures; auditor role sees read-only.
- Grievance resolve without reason is rejected and surfaced cleanly.

## Out of Scope
Member portal closure/NOC and support views (MP20 in 011x portal scope, 011NA), auditor read-only views (011O done), report exports (012B/012C).

## Evidence Required
Saved RED/GREEN frontend request/action/render output for every listed owner; role/action/blocker and
mock-removal matrices; all five trusted-browser screenshots from two passing contract runs; focused
Epic 011 reverse-consumer and configured full gates.

## Risk Level
Medium

## Acceptance Criteria
- All listed S53-S68 staff screens run on backend data with role-correct, blocker-driven actions,
  including S56 recovery decision approval.
- No mock-data reads remain in these screens.
- All gates pass; screenshots of the default case, recovery approval decision, closure blockers,
  compliance trackers, and grievance resolution saved.

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
