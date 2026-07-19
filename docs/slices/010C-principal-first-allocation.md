# Slice 010C: Principal-First Allocation

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Allocate one captured repayment atomically and exactly once, reducing principal before interest and
recording the resulting balance and immutable ledger evidence.

## User Value
Accounts and borrowers receive balances that follow the approved SOP rather than operator or browser
calculations.

## Depends On
- 010B

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_servicing_postgresql_acceptance.PrincipalFirstAllocationPostgreSQLAcceptanceTests`
- Expected tests: 1

## Source References
- `docs/source/product-requirements.md` §11.23
- `docs/source/functional-spec.md` BR-056 and §11.9 Repayment Allocation Logic
- `docs/source/data-model.md` §§19.6, 35.2
- `docs/source/api-contracts.md` §32.4
- `docs/source/codebase-design.md` §17.2
- `docs/source/security-privacy.md` §22.2
- `docs/source/test-plan.md` MOD-REP-006–008, FIN-REP-001–005, E2E-011
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md` §010C

## Concrete Requirements
1. Implement the `RepaymentAllocator` owner behind §32.4. Lock the pending repayment, loan account,
   and affected schedule/ledger state in one transaction.
2. Calculate `principal = min(amount, principal_outstanding)`, then apply only the remaining amount
   to interest. Allocate to charges only when an approved configured waterfall exists.
3. If the receipt exceeds known outstanding or the charge/excess rule is not configured, retain the
   remainder explicitly as unallocated/exception truth; never make a balance negative or silently
   choose a destination.
4. Persist one explicit allocation with before/after amounts, rule/version, actor, and timestamp;
   atomically update account/schedule outstanding and append the corresponding immutable ledger row.
5. A previously allocated receipt cannot create another allocation or ledger movement. Exact replay
   returns retained truth or conflicts according to the documented API idempotency contract.
6. Require `finance.repayment.allocate`, object scope, an eligible captured receipt, and audit both
   the allocation decision and balance transition.

## Scope Boundaries / Non-Goals
- No receipt capture, statement matching, SAP posting, reversal/correction workflow, frontend, or
  policy invention for fees, charges, or excess payments.
- Do not add interest accrual/invoice/capitalisation behavior.

## Acceptance and Reverse-Consumer Tests
- Partial receipt below principal allocates only principal; receipt crossing principal allocates the
  remainder to interest; full known outstanding reaches exact zero with one ledger row.
- Duplicate allocation, concurrent allocation, rejected/pending-invalid receipt, zero amount,
  insufficient permission, and cross-scope access produce no second financial effect.
- Excess and unconfigured-charge cases remain explicit and balances never go negative.
- Receipt/SAP facts from 010B remain intact; 010A schedule/ledger returns the exact allocation and
  running balance; Epic 009 disbursement opening balance is unchanged.
- Twice-run PostgreSQL contention proves one allocation, one balance transition, and one ledger row.

## Evidence Required
- RED/GREEN calculation matrix, API/permission/audit tests, before/after balance and ledger examples,
  database constraint evidence, twice-run PostgreSQL race evidence, and 009/010A/010B regressions.

## Risk Level
High

## Acceptance Criteria
- Principal-first allocation is backend-owned, atomic, idempotent, explicit, and cannot overdraw an
  account or duplicate a ledger movement.
- Unapproved excess/charge policy remains fail-closed and observable.
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
