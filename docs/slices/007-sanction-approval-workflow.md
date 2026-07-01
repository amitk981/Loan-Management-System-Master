# Slice 007: Sanction Approval Workflow and Registers

## Status
Not Started

## Goal
Implement approval matrix, approval cases/actions, sanction decisions, exception handling, conflict/general-meeting controls, notifications, and frontend sanction/register workflows.

## User Value
Loan approvals follow required authority thresholds, are auditable, and cannot be bypassed by unassigned or conflicted users.

## Depends On
- Slice 006

## Source References
- `docs/source/implementation-roadmap.md` section 12
- `docs/source/api-contracts.md` section 25
- `docs/source/data-model.md` approval and sanction tables
- `docs/source/auth-permissions.md`
- `docs/source/functional-spec.md`

## Screens Involved
- Sanction workbench
- Approval case detail
- Approval action modal
- Sanction decision
- Credit Sanction Register
- Exception Register
- Approval matrix settings

## Prototype Reference
- `SanctionWorkbench.tsx`
- `RegistersHub.tsx`
- `SettingsHub.tsx`
- `ApprovalPanel.tsx`

## Frontend Scope
- Wire sanction workbench and registers to backend APIs.
- Add assigned/unassigned/conflicted/returned/rejected states.
- Add approval action modal validations and immutable history display.
- Add frontend gaps for exception and general meeting evidence.

## Backend/API Scope
- Approval matrix model and APIs.
- Approval case service based on amount, loan limit exception, and conflict rules.
- Approval action APIs: approve, reject, return.
- Sanction decision service.
- Sanction/exception register APIs.
- Notification jobs for approver assignment and return.
- Audit events for all approval actions.

## Database/Model Impact
- Approval matrix rules, approval cases, approval actions, sanction decisions, exception records, general meeting approval records, notifications/workflow events.

## API Contracts
- Approval and Sanction APIs
- Register APIs

## Permissions
- CFO/Director/Sanction Committee assignment checks.
- Unassigned or conflicted users cannot approve.

## Validation Rules
- Up to INR 5 lakh requires CFO + one Director.
- Above INR 5 lakh requires CFO + two Directors.
- Exceeds loan limit requires exception reason and required approvals.
- Director/relative cases require conflict exclusion and general meeting evidence.
- Approval actions are immutable.

## Test Cases
- Threshold below/exactly/above INR 5 lakh.
- Exception approval.
- Conflicted approver blocked.
- Return/reject comments required.
- Sanction created only after required approvals.
- Register accuracy and export permission.

## Visual Acceptance Criteria
- Sanction case detail preserves prototype summary and decision density.
- Approval history and blockers are easy to scan.

## Evidence Required
- Approval matrix/service tests.
- API tests.
- Screenshots of approval case, action modal, and registers.

## Risk Level
High

## Acceptance Criteria
- Approval workflow enforces source rules.
- Sanction decision is created only after required approvals.
- Registers and audit logs are generated from source events.

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
