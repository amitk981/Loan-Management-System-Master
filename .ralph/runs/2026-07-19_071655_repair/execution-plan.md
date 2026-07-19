# Repair Execution Plan

Selected slice: `009L-epic-009-staff-workflow-and-sap-posting-closure`

## Demonstrated failure

- The authoritative backend coverage gate failed only in
  `CommunicationReceiptOwnerMigrationTests.test_receipt_row_and_schema_survive_forward_reverse_and_reapply`.
- That test migrates `disbursements` to `0007`, then builds current disbursement-advice state through
  the transfer-success endpoint. Slice 009L's current endpoint now reads the table introduced by
  `disbursements.0008`, so the historical migration schema and current runtime code are incoherent.

## Repair boundary

1. Reproduce the exact test failure with the required Ralph Python interpreter and retain RED output.
2. Fix only the migration test's schema isolation so its communications migration exercise retains
   the current disbursements schema required by the fixture; do not alter the preserved 009L product
   behavior or the historical communications migration assertions.
3. Re-run the exact test and the relevant migration-test module, retaining GREEN output.
4. Run Django check and migration-sync as focused safety gates, inspect the targeted diff, and update
   the repair risk assessment, review packet, and final summary.
5. Leave the complete backend suite and coverage rerun to the independent orchestrator.
