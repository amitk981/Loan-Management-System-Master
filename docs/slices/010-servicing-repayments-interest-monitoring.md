# Slice 010: Servicing, Repayments, Interest, and Monitoring

## Status
Not Started

## Goal
Implement repayment posting/allocation, subsidiary deduction reconciliation, interest invoices/accrual/capitalisation, DPD monitoring, reminders, MIS, and matching staff/member frontend screens.

## User Value
Accounts, Credit, CFO, and borrowers can see accurate loan servicing status, repayments, interest, overdue risk, and monitoring tasks.

## Depends On
- Slice 009

## Source References
- `docs/source/implementation-roadmap.md` section 15
- `docs/source/api-contracts.md` repayment, interest, monitoring, report sections
- `docs/source/data-model.md` servicing, finance, monitoring tables
- `docs/source/functional-spec.md`
- `docs/source/test-plan.md`

## Screens Involved
- Loan Account 360
- Repayments Hub
- Interest Management
- Monitoring Dashboard
- Direct repayment entry
- Member portal loans/repayments/direct repayment info

## Prototype Reference
- `LoanAccount360.tsx`
- `RepaymentsHub.tsx`
- `InterestManagement.tsx`
- `MonitoringDashboard.tsx`
- `RepaymentLedger.tsx`
- `MP15_MyLoans.tsx`
- `MP17_Repayments.tsx`
- `MP18_DirectRepaymentInfo.tsx`

## Frontend Scope
- Wire account, ledger, repayment, interest, DPD, reminders, and member portal servicing screens to APIs.
- Add validation, allocation explanations, empty/error/loading states.
- Preserve ledger and dashboard readability.

## Backend/API Scope
- Loan account detail/schedule/ledger APIs.
- Direct repayment posting and bank statement line support.
- Principal-first repayment allocation service.
- Subsidiary deduction reconciliation.
- Interest invoice, accrual, and capitalisation services.
- DPD service and reminder queues.
- Quarterly MIS/report snapshots where in scope.

## Database/Model Impact
- Repayments, repayment allocations, bank statement lines, repayment schedules, interest invoices, accrual entries, interest capitalisations, DPD statuses, reminders, quarterly MIS reports, portfolio snapshots.

## API Contracts
- Loan Account APIs
- Repayment APIs
- Interest APIs
- Monitoring APIs
- Report/MIS APIs as needed

## Permissions
- Accounts posts repayments.
- CFO/Accounts manage interest operations.
- Borrowers only see their own member portal loan data.

## Validation Rules
- Repayment amount positive.
- Duplicate repayment references blocked.
- Allocation follows principal-first rule unless source docs/config say otherwise.
- Interest accrual/capitalisation is idempotent.
- DPD calculation is deterministic and auditable.

## Test Cases
- Repayment allocation financial tests.
- Duplicate/idempotency tests.
- Interest invoice/accrual/capitalisation tests.
- DPD bucket tests.
- Member portal access tests.
- Frontend ledger/empty/error states.

## Visual Acceptance Criteria
- Ledger and monitoring dashboards stay dense but scannable.
- Borrower portal repayment information is mobile-friendly.

## Evidence Required
- Financial rule unit tests.
- API tests.
- Screenshots of ledger, repayment posting, interest, monitoring, and portal repayment screens.

## Risk Level
High

## Acceptance Criteria
- Servicing calculations are backend-owned and tested.
- Staff and borrower frontend screens reflect the same account truth.
- Financial idempotency and audit evidence are in place.

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
