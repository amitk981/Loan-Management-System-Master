# Slice 011: Default, Recovery, Closure, NOC, Archive, and Compliance

## Status
Not Started

## Goal
Implement default cases, grace/extension notes, non-payment notes, recovery decisions/actions, closure/NOC/security return/archive, compliance trackers, grievances, and related frontend workflows.

## User Value
The platform supports controlled delinquency management, loan closure, statutory compliance, and borrower support without losing audit evidence.

## Depends On
- Slice 010

## Source References
- `docs/source/implementation-roadmap.md` section 16
- `docs/source/api-contracts.md` default, closure, compliance, grievance sections
- `docs/source/data-model.md` default/recovery/closure/compliance tables
- `docs/source/auth-permissions.md`
- SOP PDFs under `docs/source/`

## Screens Involved
- Default/Recovery Hub
- Loan Closure Hub
- Compliance Dashboard
- Grievances
- Audit Archive
- Registers
- Member portal closure/NOC and support/grievance

## Prototype Reference
- `DefaultRecoveryHub.tsx`
- `LoanClosureHub.tsx`
- `ComplianceDashboard.tsx`
- `GrievancesHub.tsx`
- `AuditArchiveHub.tsx`
- `RegistersHub.tsx`
- `MP20_ClosureNOC.tsx`
- `MP24_SupportGrievance.tsx`

## Frontend Scope
- Wire default, recovery, closure, compliance, grievance, and member portal screens to APIs.
- Add missing approval, blocker, evidence, empty/error/loading states.
- Preserve compliance dashboards and register filters while replacing mock data.

## Backend/API Scope
- Default case opening and assessment.
- Grace/extension and non-payment note workflows.
- Recovery decision/action workflow with approval matrix support.
- Closure readiness, loan closure, NOC issue, security return, archive.
- Compliance controls/tasks/evidence, Section 186 tracker, NBFC principal test, money-lending review, KYC review.
- Grievance create/list/resolve.

## Database/Model Impact
- Default cases, assessments, extensions, non-payment notes, recovery decisions/actions, loan closures, NOCs, security returns, archive records, compliance controls/tasks/evidence, Section 186 trackers, NBFC tests, money-lending reviews, grievances.

## API Contracts
- Default APIs
- Closure APIs
- Compliance APIs
- Grievance APIs

## Permissions
- Recovery and closure actions are high-control and must follow source roles.
- Auditors get read-only views where specified.
- Borrowers see only own closure/support information.

## Validation Rules
- Recovery action cannot execute without approved decision.
- Closure requires full repayment and security return checks.
- NOC issuance requires closure readiness.
- Compliance evidence review is permissioned and audited.
- Grievance resolution requires status and reason.

## Test Cases
- Default opening and extension.
- Recovery approval/action blockers.
- Closure readiness, NOC, security return.
- Compliance tracker calculations.
- Grievance create/resolve.
- Auditor read-only and borrower object access.

## Visual Acceptance Criteria
- Default/recovery/closure screens emphasize blockers and approval state.
- Compliance trackers remain compact and reviewable.

## Evidence Required
- API/service tests.
- Screenshots of default case, closure/NOC, compliance dashboard, and grievance portal.

## Risk Level
High

## Acceptance Criteria
- Default, recovery, closure, and compliance workflows are backend-owned and audited.
- Frontend screens close prototype gaps and enforce role-specific actions.
- Borrower portal support/closure views use backend data.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
