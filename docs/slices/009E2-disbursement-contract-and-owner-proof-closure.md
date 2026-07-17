# Slice 009E2: Disbursement Contract and Owner-Proof Closure

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement

## Depends On
- 009D4
- 009E

## Runtime Capabilities

postgresql-five-race-acceptance

## Goal

Align payment initiation with the source idempotency/error/deep-module contracts and prove one
genuine owner-backed initiation from governed current source-bank and readiness facts.

## Source / Review References

- `docs/source/api-contracts.md` §§6-8, 31.1-31.2, and 45
- `docs/source/codebase-design.md` §§3, 16.3-16.4, 20, 22, 26-28, 31, 36-37, and 42
- `docs/source/integrations.md` §§9.1-9.6
- `docs/source/data-model.md` §§12.3, 19.3, 29-30, and 34
- `docs/source/auth-permissions.md` §§15.6-15.7, 18, 26.5, and 30-31
- `docs/source/functional-spec.md` M06-FR-019, M07-FR-010, and M08-FR-001 through M08-FR-006
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-17_075837_architecture_review`

## Concrete Requirements

1. Put initiation behind the source-defined `disbursements.modules.disbursement_workflow` public
   interface. Internal initiation helpers may remain private, but callers and later 009F/009G work
   must not assemble a family of competing public workflow owners or import `CHECK_SPECS`/private
   `_evidence` dictionaries.
2. Give readiness one typed initiation decision containing the exact canonical check digest and
   narrow SAP/borrower-bank/source-bank identities required by its consumer. The public readiness
   API must continue to omit private evidence, and initiation must call only the typed readiness
   interface for composite payment-gate truth. Preserve 009D4's exact applicable-document signature
   scope: unrelated current signatures do not change the decision, while any required current
   Term Sheet, Loan Agreement, PoA, tri-party, or SH-4 signer drift fails initiation closed.
3. Implement API §45.2 exactly for a duplicate idempotency key: return
   `idempotency_replayed: true` with the retained original response, without writes. Align touched
   conflicts with the stable §7/§31 machine codes; do not keep private
   `DISBURSEMENT_NOT_READY`/`DISBURSEMENT_CONFLICT` vocabulary in the public contract.
4. Re-open A-126 unless the generic SFPCL RBL `BankAccount` is backed by a real governed owner
   decision with exact activation/verification authority, audit/version evidence, and singular
   current lifecycle. Do not treat mutable owner/bank/status strings alone as governance. If the
   cited source does not name the provisioner, add the narrow configuration mechanism with no
   seeded business-role grant, record the open authority in `ASSUMPTIONS.md`, and keep production
   readiness fail-closed until an explicit grant exists.
5. Retain or generate a non-empty request id and a safe final-verification comment or digest in the
   initiation audit, workflow, and frozen action evidence. Reconcile the exact initiation row,
   audit, workflow, and CFC task before projecting CFC scope.
6. Preserve manual-bank MVP truth, exact Senior Manager Finance scope, amount/account/bank locks,
   replay/race safety, secret redaction, and zero transfer/UTR/funding/activation/advice/register/
   borrower side effects.

## Test Cases

- Build one genuine public path using real 008M7/009B3C/009D4 legal, security, approval, SAP,
  borrower-bank, source-bank, loan, and configuration owners; initiate successfully without mocking
  readiness or bank/source decisions. Add unrelated signature history and prove the same success;
  mutate each required current signer and every other current owner fact and prove zero-write denial.
- Repeat the twice-run PostgreSQL five-caller races through the real typed readiness and bank owners;
  assert one complete row/audit/workflow/task winner and no loser success identity.
- Assert exact first-success §31.2 response, exact §45.2 replay envelope, stable §7 errors for each
  blocker class, generated/supplied request-id traceability, comment digest, and unchanged task/
  audit/workflow/communication counts on every denial.
- Prove a raw SFPCL-labelled RBL row with no governed decision does not pass readiness, while one
  singular current governed decision does; missing, duplicate, inactive, changed, or cross-linked
  governance fails closed.

## Evidence Required

Failing-first API/governance probes; sanitized typed readiness and governed source-bank decisions;
real public success/denial ledger; twice-run PostgreSQL races; dependency graph; focused tests and
full configured gates.

## Risk Level
High

## Acceptance Criteria

- Public initiation obeys the exact source replay/error contract behind one deep workflow owner.
- A payment instruction cannot be created from mocked, mutable-label-only, stale, or incoherent owners.
- Every success/denial/race has complete traceable and secret-free evidence with no later-state side effects.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Database rules followed, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit delegated to the orchestrator only after passing configured gates
