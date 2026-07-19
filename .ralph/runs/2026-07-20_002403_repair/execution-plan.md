# Repair Execution Plan

Selected slice: `010D-bank-statement-matching-unmatched-receipts`

## Demonstrated Failure

- Independent PostgreSQL acceptance found exactly one test and failed twice because the manual-match
  line lock applied `FOR UPDATE` across a nullable outer join.
- The repair preserves the current uncommitted 010D implementation and changes only the demonstrated
  PostgreSQL locking defect plus current-run evidence.

## Permission and Safety Check

- Intended product edit is limited to the allowed
  `sfpcl_credit/loans/modules/bank_statement_matching.py` path.
- Current-run evidence edits are limited to
  `.ralph/runs/2026-07-20_002403_repair/**`.
- Protected paths, `docs/source/**`, mechanical state/progress/status files, and unrelated product
  behavior remain unchanged.

## Repair Loop

1. Re-run the exact declared PostgreSQL acceptance label with one expected test and retain RED output.
2. Inspect only the manual-match locking queries needed to distinguish nullable-join locking from
   receipt/constraint conflicts.
3. Apply the smallest query-shape correction, keeping the line and repayment row locks and existing
   one-to-one database constraints intact.
4. Re-run the exact PostgreSQL test for GREEN, then run the focused bank-statement API suite and
   Django check/migration-sync gates.
5. Save repair risk, review, and final summary evidence with the review result set exactly to
   `Ready for independent validation` only after focused validation is green.
