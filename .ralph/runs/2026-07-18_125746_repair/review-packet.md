# Review Packet: 2026-07-18_125746_repair

## Result
Ready for independent validation

## Slice
009H4-communications-advice-evidence-and-legacy-replay-closure

## Demonstrated Failure

The previous complete coverage gate failed
`CommunicationReceiptOwnerMigrationTests.test_receipt_row_and_schema_survive_forward_reverse_and_reapply`.
The test was green alone but failed after `ApprovalReadScopeMigrationTests`, exactly matching the
parallel worker's historical migration state. Reversing communications 0005 retained every receipt
column and constraint but moved `advice_intent_id` from the last physical position to the first.

## Repair Review

- Preserved the quarantined 009H4 production implementation and migration unchanged.
- Changed only the legacy receipt signature to sort its exact column-name set before comparison.
- Retained the newer order-insensitive detailed manifest assertions for type/null/default, foreign
  keys, unique/check/index definitions, table identity, rows, ids, and forward/reverse/reapply truth.
- Rechecked 009H5 and 009I; both remain concrete and executable, so no speculative queue edit was
  made.

## Verification

- Validator-compatible two-test sequence: RED before repair, GREEN after repair.
- Focused owner/public matrix: 40 tests pass; two declared PostgreSQL-only tests skip locally.
- Django check, migration sync, Python compilation, and `git diff --check` pass.
- Protected-path and `[DEBUG-...]` scans are empty.
- Complete coverage and PostgreSQL acceptance remain Ralph's independent gates.

## Traceability

009H4 requirement 6 requires exact schema facts across forward, reverse, and reapply. Column ordinal
position is not one of the named facts and is not stable across SQLite table rebuilds. The repaired
legacy assertion now checks the exact column set, while the 009H4 detailed manifest continues to
prove every named schema and constraint attribute.

## Recommended Next Action
Run complete independent Ralph validation. After 009H4 commits, run 009H5, then 009I and 009J in
dependency order.
