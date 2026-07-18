# Execution Plan

Selected slice: 009H4-communications-advice-evidence-and-legacy-replay-closure

## Demonstrated failure

- Preserve the quarantined 009H4 implementation and repair only the independent coverage failure in
  `CommunicationReceiptOwnerMigrationTests.test_receipt_row_and_schema_survive_forward_reverse_and_reapply`.
- Use that single migration test as the tight feedback loop. It must reproduce the receipt-column
  ordering mismatch, then pass after the smallest test-fixture or migration-proof correction.

## Diagnosis and fix boundary

1. Run the exact failing test with the mandated Ralph virtualenv and save the RED output.
2. Compare the receipt schema before 0004, after 0004, after 0005, after reverse to the declared
   boundary, and after reapply. Rank falsifiable causes before changing files.
3. Fix only the demonstrated order-sensitive migration assertion or the migration operation that
   unexpectedly changes physical schema. Do not alter production advice behavior, API contracts,
   models, frontend code, or protected files unless the schema probe proves that is necessary.
4. Re-run the exact test, its migration class, and the adjacent 009H4 migration/persistence/advice
   tests. Run Django check, migration sync, and compile checks; leave the complete coverage suite to
   Ralph's independent validator.

## Evidence and handoff

- Save RED/GREEN and focused gate logs under this repair run's `evidence/terminal-logs/`.
- Write repair-scoped changed-files, risk assessment, review packet, and final summary. Update Ralph
  progress/handoff/digest only if the repair changes durable implementation truth; retain 009H4 as
  Complete and do not modify the already-concrete next slices.
