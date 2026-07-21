# Slice 010K2: Loan Ledger Statements and Export

## Status
Not Started

## Runtime Capabilities
- `none`

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Origin
Owner-chat source-coverage audit on 2026-07-19 identified the S46 export-ledger and download-statement
actions as unowned by the executable queue.

## Goal
Generate a permission-scoped, reconciled loan-ledger statement from the canonical 010A ledger without
creating a second financial truth or leaking restricted fields.

## User Value
Accounts and authorised borrowers can download a stable statement whose rows and running balances
reconcile exactly with Loan Account 360.

## Depends On
- 010K3

## Source References
- `docs/source/screen-spec.md` S46, especially Actions and Controls
- `docs/source/api-contracts.md` loan-account and standard export/download conventions
- `docs/source/security-privacy.md` export masking and signed-download controls
- `docs/source/auth-permissions.md` loan, report/export, and borrower-own-data scope
- `docs/source/data-model.md` loan ledger and running-balance fields
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md`

## Prototype Reference
- `sfpcl-lms/src/components/loan/RepaymentLedger.tsx`
- `sfpcl-lms/src/pages/loan-accounts/LoanAccount360.tsx`

## Screens Involved
None in this slice; the 010M frontend successor owns the download controls.

## Frontend Scope
None.

## Backend/API Scope
- Add a bounded statement/export action over the canonical 010A ledger selector with stable date
  range, ordering, opening/closing balances, transaction references, and generated-at/as-of metadata.
- Reconcile every exported row and total with the paginated ledger source. Do not recompute repayments,
  interest, DPD, or balances in the exporter.
- Use the established document/storage signed-download seam, short expiry, checksum, deterministic
  idempotency, and an explicit supported format. Do not expose a permanent object-storage URL.
- Borrowers may receive only their own masked statement; staff access remains permission/object scoped.

## Database/Model Impact
None expected. Reuse existing export/document job truth; add no duplicate ledger table.

## API Contracts
Add the statement request/status/download contract to `docs/working/API_CONTRACTS.md`, reusing standard
errors, idempotency, signed-download, and expiry conventions.

## Permissions
Require loan-ledger read plus the narrow export/download authority; borrower sessions require exact
own-loan scope. Sensitive export authority is not implied.

## Audit Requirements
Audit request, generation outcome, and download with loan/job/checksum references, never statement
rows, raw bank data, or signed URLs.

## Validation Rules
- Opening balance + movements equals closing balance for each supported range.
- Filters, selector rows, file rows, totals, and status response must agree.
- Expired, revoked, cross-user, cross-loan, and guessed-job downloads deny safely.

## Test Cases
- RED then GREEN: statement rows/totals reconcile with 010A ledger for empty, partial-range, and full
  history cases; supported file parses and checksum matches.
- Permission, borrower-own-data, masking, expiry, idempotency, and audit tests.
- Reversal/adjustment rows from 010C2 remain explicit compensating entries rather than rewritten history.

## Visual Acceptance Criteria
Not applicable (backend only).

## Evidence Required
Saved RED/GREEN output; parsed statement and reconciliation matrix; permission/masking/expiry examples;
signed-download and audit evidence; reverse-consumer and full gates.

## Risk Level
High

## Acceptance Criteria
- Downloaded statements exactly reconcile with canonical immutable ledger truth.
- Access is scoped, masked, expiring, audited, and cannot expose permanent storage URLs.
- No duplicate financial calculation or ledger storage is introduced.

## Done Checklist
- [ ] Execution plan written
- [ ] TDD RED/GREEN evidence saved
- [ ] Contract and implementation completed
- [ ] Reconciliation, permissions, masking, download, and audit tested
- [ ] Full gates passed
- [ ] Risk and review evidence completed
- [ ] Commit delegated to the orchestrator after gates
