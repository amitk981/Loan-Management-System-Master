# Slice 010F: Interest Invoice Generation

## Status
Complete

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Generate and issue one annual interest invoice from frozen loan/rate/accounting truth while preserving
historical calculations, document/communication evidence, and configurable ownership.

## User Value
Borrowers and Finance receive a reproducible year-end interest demand rather than a client-supplied or
later-rate-dependent amount.

## Depends On
- 010E3

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_servicing_postgresql_acceptance.InterestInvoicePostgreSQLAcceptanceTests`
- Expected tests: 1

## Source References
- `docs/source/product-requirements.md` §11.24
- `docs/source/user-flows.md` §§29.3, 29.6
- `docs/source/functional-spec.md` BR-060/064/065 and §11.10
- `docs/source/domain-model.md` §13.5 and Important Ownership Clarification
- `docs/source/data-model.md` §§18.5, 19.7
- `docs/source/api-contracts.md` §§33.1–33.3
- `docs/source/codebase-design.md` §17.3
- `docs/source/auth-permissions.md` §§12.9, 26.6, 40.4
- `docs/source/test-plan.md` MOD-INT-001/002/010, FIN-INT-001/002/010
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md` §010F

## Concrete Requirements
1. Implement annual draft generation through the canonical interest owner for an eligible loan and
   financial-year period. The service—not the caller—derives principal base, effective rate snapshots,
   period, paid/unpaid interest, and invoice amount.
2. Freeze loan, member, financial year, period, principal base, rate/rate-source version, calculation
   configuration/version, amount, invoice identity, and generation actor/time on the invoice.
3. Prevent an unapproved duplicate invoice for the same loan/period. Exact request replay returns
   retained truth; changed inputs or later rate changes cannot rewrite the historical invoice.
4. Missing benchmark/spread/day-count/tax/fee configuration required by the calculation fails closed
   with no invoice. Keep issue-owner permission configurable because source ownership is unresolved;
   do not hard-code Sales, Credit, or Accounts as sole owner.
5. Issue only a valid draft through existing document/communications seams, retaining invoice file,
   communication/job, recipient-safe delivery status, actor, and audit truth. Issuance cannot silently
   mark the invoice paid.
6. Enforce create/issue permissions and loan object scope; keep borrower PII out of logs/errors.

## Scope Boundaries / Non-Goals
- No monthly accrual (`010G`), capitalisation (`010H`), payment allocation, rate-policy invention,
  invoice payment/reversal workflow, bulk UI, or frontend wiring.
- Do not let the §33.1 example request make client-supplied monetary fields authoritative; update the
  repository API contract to the implemented backend-owned calculation contract.

## Acceptance and Reverse-Consumer Tests
- Year-end generation uses the correct principal and effective historical rate and returns one draft;
  issuing binds one document/communication evidence chain.
- Same-period duplicate/concurrent requests, changed replay, missing required rate configuration,
  closed/ineligible loan period, wrong permission/owner configuration, and cross-scope access fail
  without duplicate invoice or communication.
- A later rate change leaves the retained invoice byte-for-byte unchanged; 010A ledger/account reads
  remain unchanged by draft generation and expose only source-owned invoice movement when defined.
- Existing communications idempotency/provider tests and repayment balances remain green.

## Evidence Required
- RED/GREEN calculation fixtures with rate changes and FY boundaries, API/permission/audit tests,
  invoice/document/communication evidence, database duplicate proof, PostgreSQL same-period race,
  and 009 communications plus 010A–010E reverse-consumer results.

## Risk Level
High

## Acceptance Criteria
- Annual invoice calculations are backend-owned, rate-snapshot-bound, duplicate-safe, immutable, and
  issued only through configured authority with retained evidence.
- Open accounting and ownership policy is not guessed.
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
