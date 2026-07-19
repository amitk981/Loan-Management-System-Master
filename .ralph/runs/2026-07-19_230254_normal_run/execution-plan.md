# Execution Plan

Selected slice: 010C-principal-first-allocation

## Scope and interface

- Add the documented `POST /api/v1/repayments/{repayment_id}/allocate/` interface.
- Keep the financial implementation behind one `RepaymentAllocator.allocate` module interface.
- Add only the allocation, immutable ledger, audit, and balance persistence required by 010C; no
  frontend, capture, SAP, reversal, interest-accrual, invoice, or charge-policy work.

## Red/green sequence

1. RED: add one public-interface test for a partial receipt below principal, including permission,
   before/after balance, allocation evidence, audit evidence, and the 010A ledger projection.
2. GREEN: add the minimum models/migration, allocator module, route, and view needed for that path.
3. RED/GREEN: extend the public-interface matrix for principal-to-interest crossing, exact payoff,
   explicit excess/unconfigured-charge remainder, exact replay, invalid state, permission, and scope.
4. RED/GREEN: add database constraint and append-only evidence tests.
5. Add the declared PostgreSQL five-request contention acceptance proving one allocation, one account
   transition, and one ledger row; collection is local evidence and the orchestrator runs it twice on
   PostgreSQL.

## Financial rules

- Principal allocation is `min(receipt, principal_outstanding)`.
- Interest allocation is `min(receipt - principal allocation, interest_outstanding)`.
- Charges allocation remains zero because no approved waterfall is configured.
- Any remainder is retained as `unallocated_amount` with explicit exception status; no outstanding
  amount may become negative.
- Receipt/account/schedule state is locked in one transaction. A one-to-one allocation constraint and
  one-to-one ledger link provide database-level duplicate protection.

## Verification and evidence

- Save focused RED and GREEN backend outputs under `evidence/terminal-logs/` using the mandated venv.
- Run focused 009/010A/010B reverse-consumer tests, backend check, migration sync, and PostgreSQL test
  collection. Do not run the complete backend suite or coverage locally.
- Update the working API contract, then complete `risk-assessment.md`, `final-summary.md`, and
  `review-packet.md` with traceability and the exact ready result.
