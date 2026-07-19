# Slice 010A: Loan Account Schedule and Ledger

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Establish backend-owned repayment-schedule and immutable loan-ledger read truth for an existing loan
account, ready for later repayment and interest slices to append their movements.

## User Value
Accounts and Credit can inspect the due schedule and reconcile every financial movement without
calculating balances in the browser.

## Depends On
- 009J
- 009L
- 009L3
- CR-012

## Runtime Capabilities

- `none`

## Source References
- `docs/source/product-requirements.md` §11.21
- `docs/source/data-model.md` §§18.1–18.4
- `docs/source/api-contracts.md` §30 (extend the contract for schedule/ledger reads)
- `docs/source/screen-spec.md` S42, S43, S46
- `docs/source/implementation-roadmap.md` §§15.2–15.4
- `docs/source/test-plan.md` §20.2
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md` §010A

## Concrete Requirements
1. Represent repayment-schedule lines with the source fields and the unique
   `(loan_account, installment_number)` rule. Dates and amounts come from approved loan terms; do
   not invent an amortisation policy that the source does not define.
2. Provide permission- and object-scoped, paginated schedule and ledger read APIs for a loan account.
   Define their exact request/response/error shapes in the repository API contract.
3. The ledger projection has deterministic ordering and exposes transaction date/type, owner
   reference, debit/credit, principal/interest/total running balances, actor, SAP status, and remarks.
4. Build ledger rows from canonical owner records (including the successful disbursement already
   available from Epic 009) or an append-only ledger model. Never copy mutable browser totals or
   allow update/delete of posted history.
5. Keep schedule/ledger reads query-bounded and stable under pagination. Money remains decimal and
   balances cannot be negative.
6. Enforce `finance.loan_account.read` and the loan-account scopes in auth §19.3; mutation endpoints
   are not introduced here.

## Scope Boundaries / Non-Goals
- No repayment capture/allocation, SAP receipt posting, reversal workflow, interest calculation,
  DPD calculation, statement export, or frontend wiring.
- Do not change Epic 009 loan creation, disbursement success, or account-activation rules.
- A source-silent recurring schedule generator is out of scope; retain approved term-sheet truth.

## Acceptance and Reverse-Consumer Tests
- Active account returns ordered schedule lines and a ledger containing its single successful
  disbursement with exact opening/running balances.
- Empty schedule/ledger, pagination boundaries, object-not-found, unauthenticated, forbidden-role,
  and cross-scope account access are covered.
- Duplicate installment number and negative schedule/balance data are database/service rejected.
- Existing loan-account detail, status-history, disbursement-success, and 009J staff read tests remain
  green; a ledger read cannot mutate source rows.

## Evidence Required
- RED/GREEN unit/service/API evidence, migration constraint evidence if schema changes, API response
  examples, query-count evidence for a populated ledger, and focused 009 reverse-consumer results.

## Risk Level
Medium

## Acceptance Criteria
- Schedule and ledger endpoints expose one permission-correct backend truth with deterministic
  ordering and decimal running balances.
- Financial history is append-only and existing Epic 009 account/disbursement behavior is unchanged.
- Required focused, reverse-consumer, and full gates pass.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested, if needed
- [ ] Audit events tested, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Substantive risks/decisions recorded in `review-packet.md` (and HANDOFF only when needed)
- [ ] Commit created only after passing gates
