# Slice 010H: Interest Capitalisation after 30 April

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Preview and then capitalise eligible unpaid interest once after 30 April, atomically increasing
principal and retaining the calculation, ledger, borrower-intimation, and audit evidence.

## User Value
Finance applies the approved annual rule consistently, and borrowers can trace why principal changed.

## Depends On
- 010G

## Source References
- `docs/source/product-requirements.md` §11.24
- `docs/source/user-flows.md` §§29.5–29.6
- `docs/source/functional-spec.md` BR-061–063 and §11.10 M10-FR-007–010
- `docs/source/data-model.md` §§19.9, 35.3
- `docs/source/api-contracts.md` §§33.6–33.7, 45
- `docs/source/screen-spec.md` S49
- `docs/source/component-spec.md` §15.6
- `docs/source/codebase-design.md` §17.3
- `docs/source/test-plan.md` MOD-INT-005–009, FIN-INT-005–009, E2E-013
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md` §010H

## Concrete Requirements
1. Implement a dry-run eligibility check that derives unpaid eligible invoice/interest truth as of
   the end of 30 April and returns reasons/old/new principal without any financial, communication,
   audit-finalisation, or idempotency-consumption write.
2. Final capitalisation requires a date after 30 April, `finance.interest_capitalise`, loan scope,
   one bounded `Idempotency-Key`, and locked current loan/invoice/accrual truth. The caller cannot
   choose the unpaid amount or revised principal.
3. Atomically create one `(loan, financial_year)` capitalisation, increase principal by exactly the
   eligible unpaid interest, update account/schedule truth, mark the related interest state, and
   append one immutable ledger movement with old/new balances.
4. Store financial year, eligibility/as-of date, old principal, unpaid amount, new principal, rate/
   calculation versions, actor, and timestamp. New-FY interest subsequently uses the revised base;
   historical invoice/accrual snapshots do not change.
5. Queue an official email and generate/bind a hard-copy letter task/artifact through existing
   communications/documents owners. Preserve pending/sent/failed truth; never claim notification
   merely because the capitalisation committed.
6. Exact replay returns the retained chain. Changed/cross-loan replay, concurrent finalisation,
   partial provider failure, or retry cannot create a second principal/ledger movement.

## Scope Boundaries / Non-Goals
- No invoice/accrual recalculation, interest-rate administration, approval rule not present in source,
  frontend wiring, or direct provider call from the finance owner.
- Do not capitalise before/at the 30-April cutoff or without eligible unpaid interest.

## Acceptance and Reverse-Consumer Tests
- Dry run is zero-write; 1 May finalisation changes principal by the exact unpaid amount once and
  retains one ledger, email job, hard-copy task/artifact, and audit chain.
- Before/on cutoff, paid/zero interest, duplicate FY, changed replay, wrong permission, cross-scope
  loan, missing invoice/configuration, and provider failure cannot duplicate or partially move money.
- PostgreSQL concurrent callers produce one capitalisation and balance movement.
- 010F invoice and 010G accrual snapshots remain immutable; 010A ledger/account returns exact new
  principal; communications retry does not re-capitalise.

## Evidence Required
- RED/GREEN cutoff/FY/paid-unpaid calculation matrix, API/permission/audit tests, database unique and
  transaction proof, twice-run PostgreSQL race, ledger before/after, communication/document evidence,
  and 009 communications plus 010A/010F/010G reverse-consumer results.

## Risk Level
High

## Acceptance Criteria
- Eligible unpaid interest is capitalised only after 30 April, exactly once, from backend truth and
  with atomic principal/ledger evidence.
- Borrower-intimation obligations are durable and honestly reported.
- Required focused, contention, reverse-consumer, and full gates pass.

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
