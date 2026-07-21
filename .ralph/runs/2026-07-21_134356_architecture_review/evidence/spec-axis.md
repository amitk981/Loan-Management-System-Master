# Spec Axis

The review compared each product diff with its slice requirements and cited Epic 010 digest/source contracts.

## Binding High gaps

- 010K3 requirement 2 promises a final execution-time serviceability owner. The dispatcher releases the check transaction before the adapter side effect, and the review probe sends after a committed repayment.
- 010K3 requirements 3-4 promise immutable cutoff decisions and source-write races. A post-cutoff issuance of an older-dated invoice changes a subsequently generated historical report because the current invoice status is serialized.
- 010MA requires one stable idempotent repayment attempt with truthful retry. Its client-side three-call coordinator cannot resume after capture succeeds and SAP/allocation fails.

## Medium gaps bundled into Epic 010 closure

- 010L requirement 2 asks for paginated canonical collections; its portal API consumes only page 1 with page size 100.
- 010K2's borrower export projection contains staff/internal servicing fields and its empty CSV lacks retained statement metadata.
- 010K2 concurrent statement replay and 010K3 date/batch matrices are not demonstrated by permanent tests.

## Satisfied closure

- 010K3 provides the bidirectional DPD database guard and public capitalisation-aware source decision required to close `AR-010-DPD-001`.
