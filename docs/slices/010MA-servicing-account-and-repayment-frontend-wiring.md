# Slice 010MA: Servicing Account and Repayment Frontend Wiring

## Status
Complete

## Origin
Oversized slice: `010M`

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Wire the staff account schedule/ledger and repayment/reconciliation surfaces from oversized 010M:
Loan Account 360 schedule and ledger views (S43/S46), direct repayment entry (S44), bank-statement
exceptions, and subsidiary deduction reconciliation (S45).

## User Value
Accounts staff can inspect canonical schedules and ledgers, post a real direct repayment, see the
backend allocation, and reconcile statement and subsidiary evidence without mock financial data.

## Depends On
- 010L

## Runtime Capabilities

- `localhost-e2e-server`

## Trusted Browser Acceptance

- Spec: `e2e/servicing-monitoring-workflows.e2e.spec.ts`
- Screenshot: `servicing-ledger.png`
- Screenshot: `direct-repayment-posting.png`

## Source References
- docs/source/screen-spec.md screens S43-S46 and section 9.7 (repayment rules)
- docs/source/api-contracts.md sections 32 (repayment) and 45 (idempotency contract)
- docs/source/functional-spec.md BR rules for principal-first allocation
- docs/source/test-plan.md (financial calculation test expectations)
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md` shared invariants and
  §010M–010O

## Prototype Reference
- sfpcl-lms/src/pages/repayments/RepaymentsHub.tsx
- sfpcl-lms/src/pages/loan-accounts/LoanAccount360.tsx (ledger/schedule tabs)
- sfpcl-lms/src/components/loan/RepaymentLedger.tsx

## Concrete Requirements
1. Establish the shared servicing transport seam needed by this slice and 010MB using the standard
   response/error/pagination contracts. It must propagate validation, 401/403, and backend errors;
   displayed money, balances, allocation, and state remain backend-owned Money projections.
2. Wire `LoanAccount360.tsx` schedule/ledger tabs and `RepaymentLedger` to 010A APIs, including
   deterministic pagination for long schedules/ledgers and refresh after a successful posting.
3. Wire `RepaymentsHub.tsx` direct repayment capture through the canonical 010B/010C flow. Where a
   combined SAP-post-and-allocate action is exposed, require both canonical permissions. Send one
   caller-stable `Idempotency-Key` per attempted action, display the backend principal-first
   allocation explanation, preserve exact replay, and show duplicate/validation denial cleanly
   without a second client mutation.
4. Wire the 010D bank-statement matching/unmatched-receipt queue and the 010E subsidiary deduction
   reconciliation view from retained backend projections. Add only the scoped canonical repayment
   read projection needed by S45 if it is absent; do not duplicate allocation/domain ownership in
   a frontend or read view.
5. Use the existing prototype components and patterns without new styling. Supply loading, empty,
   error, unauthorised, validation, and success states for every owned read/mutation surface.

## Owned Mock Removals
This successor inherits 010M's final-removal ownership for these files. After it, none may import
`src/data/mockData.ts` or keep inline production business fixtures:
- `src/pages/repayments/RepaymentsHub.tsx`
- `src/pages/loan-accounts/LoanAccount360.tsx` (initial wiring by 009J; final removal here)
- `src/components/loan/RepaymentLedger.tsx`

## Test Cases
- Paginated schedules and ledgers render backend values, preserve backend totals, and page without
  client-owned money calculations.
- Posting a repayment sends one stable idempotency key, shows the backend allocation breakdown
  (principal first), and refreshes canonical ledger truth.
- Duplicate repayment reference shows the backend rejection cleanly; exact idempotent replay does
  not double-post or issue a second client mutation.
- Statement exception and subsidiary queues render canonical rows plus loading, empty, error, and
  unauthorised states without local matching or allocation policy.
- The three owned production files contain no mock import or inline production business fixture.

## Out of Scope
Interest invoice/accrual/capitalisation and DPD/reminder monitoring (010MB), member portal loan views
(010L done), CFO quarterly MIS backend (010K), default workflows (011x), and global search (010N).

## Evidence Required
Saved RED/GREEN servicing-transport and account/repayment component results; exact envelope,
pagination, Money, permission, idempotency, replay/duplicate, validation/error, refresh, and mock-
removal evidence; backend RED/GREEN evidence for any scoped repayment read projection; focused
reverse-consumer and configured frontend/backend gates; and both trusted-browser screenshots from
two passing contract runs using real backend login/current-user authority without an auth mock.

## Retained Failed-Run Evidence Allocation
- Retained run `.ralph/runs/2026-07-21_102540_normal_run/` is a requirements map only; failed-
  candidate code is not acceptance evidence and this successor must recreate every assigned proof.
- Reproduce the account/repayment portions of `servicing-api-red.log`, `servicing-api-green.log`,
  `servicing-workspaces-red.log`, `servicing-workspaces-green.log`, and the final focused frontend
  result. Recreate the repayment portion of `backend-read-projections-red.log`/`green.log`, the
  direct-repayment impacted tests, and the deterministic real-auth seed proof when backend support
  is needed.
- Recreate the `servicing-ledger.png` and `direct-repayment-posting.png` assertions from the retained
  four-scenario Playwright collection. Re-run typecheck, lint, build, mock/auth static audits, and
  all risk-selected gates in this successor's own run folder.

## Predicted Diff Budget
Target 850-1,200 changed lines across the shared transport foundation, three owned production
surfaces, any narrow repayment read projection, focused tests, documentation, and the two-scenario
browser contract. Stop and resplit before implementation if the forecast exceeds 1,450 lines. This
is comfortably below the configured 2,000-line limit and leaves interest/monitoring to 010MB.

## Risk Level
High

## Material Risks
- Client-calculated money, balances, allocation, or match decisions diverging from ledger truth.
- A duplicate/replayed repayment causing a second financial movement or stale ledger display.
- SAP-post/allocation authority being widened, or 401/403/404 object-scope behavior being obscured.
- Statement or subsidiary evidence exposing another loan/member or implying an allocation it did
  not canonically retain.
- Pagination or refresh behavior omitting, duplicating, or reordering financial history.

## Acceptance Criteria
- S43-S46 account and repayment surfaces run on canonical backend data; a repayment posted in the
  UI lands in the real ledger with the exact backend allocation shown after refresh.
- Replay/duplicate, permission, validation, pagination, and error behavior are proved without
  client-owned financial or matching policy.
- All three inherited mock-removal owners are clean; configured gates and both twice-run browser
  screenshot contracts pass independently.

## Done Checklist
- [ ] Execution plan written
- [ ] Failing service/component and any backend read-projection tests written first
- [ ] Account schedule/ledger and repayment/reconciliation wiring implemented
- [ ] API contracts updated if a scoped repayment read projection is added
- [ ] Permissions, idempotency, replay, validation, and mock-removal behavior tested
- [ ] Trusted browser evidence saved from two passing runs
- [ ] Tests/typecheck/lint/build and all risk-selected gates passed
- [ ] Risk assessment and review packet completed
- [ ] Commit delegated to the orchestrator after gates
