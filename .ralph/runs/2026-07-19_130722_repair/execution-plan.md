# Execution Plan

Selected slice: 009L5-epic-009-exact-selector-and-consumer-parity-closure

## Demonstrated failure

- Independent full coverage reached 18 historical migration-test errors on SQLite.
- Every retained traceback ends in the new disbursements `0010` `CryptoExtension` reverse path
  querying PostgreSQL's `pg_extension` table through SQLite.
- Preserve the existing 009L5 selector/consumer implementation and repair only this migration's
  database-vendor boundary.

## Tight feedback loop

1. Run one existing historical migration regression with the mandated Ralph interpreter and save
   the expected `no such table: pg_extension` RED output.
2. Make the `pgcrypto` migration explicitly PostgreSQL-only while retaining reversible extension
   creation/removal on PostgreSQL and a no-op on SQLite.
3. Re-run the exact regression GREEN, then run the other migration-heavy labels named by the
   independent failure plus the slice's focused selector labels.

## Verification and evidence

- Save RED/GREEN and migration-sync output under this repair run's `evidence/terminal-logs/`.
- Run Django check, the focused historical migration regressions, and focused 009L5 tests; do not
  run the complete suite or coverage because Ralph owns authoritative revalidation.
- Inspect only the migration hunk and diff stats, then complete `risk-assessment.md`,
  `review-packet.md`, and `final-summary.md` with the repair cause and residual PostgreSQL risk.
- Leave state, slice status, changed-files, commit, merge, and push to the Ralph orchestrator.
