# Slice 010E: Subsidiary Deduction Reconciliation

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Capture and reconcile a subsidiary produce-payment deduction with its agreement, transfer, statement,
Treasury-verification, allocation, and SAP-status evidence kept distinct and auditable.

## User Value
Borrowers receive credit for genuine subsidiary deductions while unclear or unsupported deductions
remain visible for review instead of changing balances automatically.

## Depends On
- 010D2

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_servicing_postgresql_acceptance.SubsidiaryDeductionPostgreSQLAcceptanceTests`
- Expected tests: 2

## Source References
- `docs/source/product-requirements.md` §11.23
- `docs/source/user-flows.md` §28
- `docs/source/functional-spec.md` BR-058/059 and §11.9
- `docs/source/domain-model.md` §13.4
- `docs/source/data-model.md` §§19.5–19.6
- `docs/source/api-contracts.md` §§32.3–32.5, 45
- `docs/source/screen-spec.md` S45
- `docs/source/security-privacy.md` §§22.2, 23.1
- `docs/source/test-plan.md` MOD-REP-003/004, INT-SUB-001–007, E2E-012
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md` §010E

## Concrete Requirements
1. Extend the canonical repayment-capture owner for `subsidiary_deduction`. Require positive amount,
   received date, subsidiary company, produce/payment reference, transfer/bank reference, actor, and
   bounded `Idempotency-Key`; enforce duplicate subsidiary/transfer references.
2. Verify the applicable tri-party agreement through the existing agreement/document owner before a
   receipt may become reconcilable. A missing agreement is an explicit blocked/exception result, not
   an inferred approval.
3. Require borrower name and loan application/account reference in statement truth for auto-match.
   Missing or conflicting facts preserve the receipt/line as unmatched exception for authorised
   manual reconciliation; they must not auto-allocate.
4. Bind the receipt to the 010D statement line and retain subsidiary, produce-payment, Treasury
   verification, and SAP posting facts separately. Treasury verification must precede SAP marking.
5. Reuse 010C for allocation after reconciliation. Do not reimplement the principal-first rule or
   directly edit balances/ledger from this module.
6. Enforce `finance.repayment.create/allocate/mark_sap_posted`, object scope, and §26.6 role truth;
   audit capture, match/exception, verification, allocation request, and SAP transition.

## Scope Boundaries / Non-Goals
- No subsidiary payment calculation, agreement creation, bank integration, transaction split policy,
  custom allocation rule, borrower acknowledgement, or frontend wiring.
- Amount above known outstanding remains an explicit excess exception under the open policy.

## Acceptance and Reverse-Consumer Tests
- Valid agreement + exact narration/line creates one reconciled subsidiary receipt that can invoke
  the retained 010C allocation and later record SAP reference.
- Missing agreement, missing/mismatched borrower or application reference, duplicate deduction/
  transfer reference, negative amount, ambiguous line, excess amount, wrong role, and cross-scope
  access produce no unauthorised allocation or balance change.
- Treasury verification is required before SAP posting; exact replay is zero-write; concurrent same
  reference retains one receipt, one match, and at most one allocation.
- Direct receipts from 010B and generic matching from 010D retain their existing behavior.

## Evidence Required
- RED/GREEN service/API/permission/audit tests, full INT-SUB/E2E-012 matrix, agreement and statement
  fixtures, PostgreSQL duplicate/reconcile race evidence, retained 010C balance/ledger proof, and
  010B/010D reverse-consumer results.

## Risk Level
Medium

## Acceptance Criteria
- A subsidiary receipt cannot affect balances without agreement, unambiguous or authorised matching,
  and the canonical allocation owner.
- Duplicate, exception, Treasury, SAP, and audit truth are explicit and permission-correct.
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
