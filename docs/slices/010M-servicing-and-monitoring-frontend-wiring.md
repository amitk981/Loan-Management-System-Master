# Slice 010M: Servicing and Monitoring Frontend Wiring

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Wire the staff servicing screens to the backend built in 010A-010K: Repayments Hub with direct repayment entry (S44), subsidiary deduction reconciliation (S45), loan ledger and schedule views (S43/S46) inside Loan Account 360, Interest Management (S47-S49), and the Monitoring Dashboard with DPD and reminders (S50-S52).

## User Value
Accounts, Credit, and CFO work real repayments, interest runs, and overdue monitoring — the financial heart of servicing stops being a mock-up.

## Depends On
- 010L

## Runtime Capabilities

- `localhost-e2e-server`

## Trusted Browser Acceptance

- Spec: `e2e/servicing-monitoring-workflows.e2e.spec.ts`
- Screenshot: `servicing-ledger.png`
- Screenshot: `direct-repayment-posting.png`
- Screenshot: `interest-management.png`
- Screenshot: `monitoring-dashboard.png`

## Source References
- docs/source/screen-spec.md screens S43-S52 and sections 9.7 (repayment rules), 9.8 (interest rules)
- docs/source/api-contracts.md sections 32 (repayment), 33 (interest), 34 (monitoring/reminders), 45 (idempotency contract)
- docs/source/functional-spec.md BR rules for principal-first allocation and 30-April capitalisation
- docs/source/test-plan.md (financial calculation test expectations)
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md` §010M–010O

## Prototype Reference
- sfpcl-lms/src/pages/repayments/RepaymentsHub.tsx
- sfpcl-lms/src/pages/interest/InterestManagement.tsx
- sfpcl-lms/src/pages/monitoring/MonitoringDashboard.tsx
- sfpcl-lms/src/pages/loan-accounts/LoanAccount360.tsx (ledger/schedule tabs)
- sfpcl-lms/src/components/loan/RepaymentLedger.tsx

## Concrete Requirements
1. Wire `RepaymentsHub.tsx`: direct repayment posting form (010B) with `Idempotency-Key` per api-contracts §45, allocation explanation display (principal-first, 010C), bank statement matching/unmatched receipts queue (010D), and subsidiary deduction reconciliation view (010E).
2. Wire ledger and schedule tabs in `LoanAccount360.tsx`/`RepaymentLedger` to 010A APIs with pagination for long ledgers.
3. Wire `InterestManagement.tsx`: invoice list/generation state (010F), accrual run status (010G), capitalisation view (010H) — run-trigger actions only for permitted roles.
4. Wire `MonitoringDashboard.tsx`: DPD buckets (010I), reminder queue (010J) with existing KPI/queue patterns.
5. Money values use the Money type; loading, empty, error, unauthorized, validation states throughout.

## Owned Mock Removals
This slice is the final owner of these files' mock surface — after it, none of them may import `src/data/mockData.ts` or keep inline business fixtures:
- `src/pages/repayments/RepaymentsHub.tsx`
- `src/pages/monitoring/MonitoringDashboard.tsx`
- `src/pages/loan-accounts/LoanAccount360.tsx` (initial wiring by 009J; final removal here)
- `src/components/loan/RepaymentLedger.tsx`

## Test Cases
- Posting a repayment shows the backend allocation breakdown (principal-first) and refreshes the ledger.
- Duplicate repayment reference shows the backend rejection cleanly; idempotent replay does not double-post.
- DPD buckets and reminder queue match seeded fixtures.
- Non-permitted role cannot trigger accrual/capitalisation (frontend + 403).

## Out of Scope
Member portal loan views (010L done), CFO quarterly MIS backend (010K), default case workflows (011x), global search (010N).

## Evidence Required
Saved RED/GREEN frontend service/component results for every wired owner; exact request, permission,
idempotency, error-state, and mock-removal evidence; all four trusted-browser screenshots from two
passing contract runs; focused reverse-consumer and configured full gates.

## Risk Level
High

## Acceptance Criteria
- S43-S52 surfaces run on backend data; a repayment posted in the UI lands in the real ledger with correct allocation shown.
- No mock-data reads remain in servicing/monitoring screens.
- All gates pass; screenshots of ledger, posting flow, interest, and monitoring saved.

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
