# Slice 010B: Direct Repayment Posting

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Capture a confirmed direct borrower RTGS/NEFT receipt exactly once, with bank evidence, audit truth,
pending allocation, and the next-working-day SAP-posting obligation.

## User Value
Accounts and Credit can safely register real bank receipts without duplicates or premature balance
changes.

## Depends On
- 010A

## Source References
- `docs/source/product-requirements.md` §11.23
- `docs/source/user-flows.md` §27
- `docs/source/functional-spec.md` BR-055/057 and §11.9
- `docs/source/domain-model.md` §13.4
- `docs/source/data-model.md` §19.5
- `docs/source/api-contracts.md` §§32.2, 32.5, 45
- `docs/source/auth-permissions.md` §§12.9, 20.2, 26.6
- `docs/source/security-privacy.md` §22.2
- `docs/source/test-plan.md` MOD-REP-001/002/005/009, API-REP-001/003, E2E-011
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md` §010B

## Concrete Requirements
1. Implement the source-shaped direct-repayment capture through the repayment-capture owner. Require
   a serviceable loan, positive decimal amount, received date, RTGS/NEFT method, bank reference,
   evidence link where supplied, remarks, actor, and a nonblank bounded `Idempotency-Key`.
2. Enforce the canonical duplicate bank-reference rule at both service/database boundaries. An exact
   idempotency replay returns the retained result; a changed or cross-loan use conflicts before any
   repayment/audit/task write.
3. Store source `direct_farmer`, allocation `pending`, and SAP posting `pending`. Capture alone must
   not change principal, interest, schedule, or ledger balances; `010C` owns that transition.
4. Create or expose a durable next-working-day SAP posting obligation/status without pretending SAP
   is integrated. Marking posted requires the source SAP reference, actor, timestamp, permission,
   and audit event through the §32.5 contract.
5. Restrict capture to `finance.repayment.create` and SAP marking to
   `finance.repayment.mark_sap_posted`, with §19.3 loan-object scope.
6. Audit receipt creation and SAP-status transition without logging sensitive evidence content.

## Scope Boundaries / Non-Goals
- No allocation or balance/ledger mutation (`010C`), bank-statement import/matching (`010D`),
  subsidiary receipt (`010E`), provider integration, reversal, acknowledgement, or frontend work.
- Do not accept cash/cheque/unspecified modes for this source-defined direct path.

## Acceptance and Reverse-Consumer Tests
- A valid RTGS/NEFT request creates one pending receipt and SAP obligation; exact replay creates no
  extra row/event/task.
- Duplicate bank reference, changed replay, zero/negative amount, unsupported mode, closed or
  pre-disbursement loan, wrong permission, and cross-scope account all fail without financial writes.
- SAP-posted transition requires reference and permission, is audit-visible, and cannot fabricate a
  second receipt or allocation.
- Existing 010A schedule/ledger and Epic 009 loan/disbursement tests remain unchanged after capture.
- PostgreSQL concurrent same-key and same-reference requests retain one receipt and one obligation.

## Evidence Required
- RED/GREEN financial/service/API/permission tests, database uniqueness proof, twice-run PostgreSQL
  concurrency evidence, audit/task evidence, API response examples, and focused 009/010A regression.

## Risk Level
High

## Acceptance Criteria
- Direct receipts are positive, permission-correct, duplicate-safe, idempotent, auditable, and remain
  pending until the separately owned allocation occurs.
- SAP posting truth is recorded without claiming external SAP automation.
- Required focused, concurrency, reverse-consumer, and full gates pass.

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
