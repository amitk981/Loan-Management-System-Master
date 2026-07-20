# Review Packet: 2026-07-20_050833_repair

## Result
Ready for independent validation

## Slice
010E2-effective-rate-versioning-and-borrower-notices

## Demonstrated Failure

The normal run's complete coverage gate reported five errors in two historical migration-test
classes. A focused rerun reproduced the same five errors with exit code 1; see
`evidence/terminal-logs/migration-regression-red.log`.

## Root Cause and Repair

The new `configurations.0006` graph leaf depends transitively on current loan, application, and
credit state. Two legacy migration tests projected all non-excluded leaves after physically rolling
the application schema backward, but did not exclude the configuration owner. Their in-memory
models therefore outran the rolled-back tables. The repair adds `configurations` to both existing
downstream-owner exclusion sets. No production or slice behavior changed.

## Validation Evidence

- Exact failed classes: 5 tests passed, exit code 0 —
  `evidence/terminal-logs/migration-regression-green.log`.
- 010E2 API/service module: 8 tests run, 5 passed and 3 PostgreSQL-only skips, exit code 0 —
  `evidence/terminal-logs/interest-rate-focused-green.log`.
- Django system check passed — `evidence/terminal-logs/backend-check-green.log`.
- Migration sync passed with no changes detected —
  `evidence/terminal-logs/migration-sync-green.log`.
- Diagnosis and causal proof are summarized in `evidence/repair-diagnosis.md`.

## Review Focus

- Confirm `configurations.0006` remains a legitimate dependency leaf for its loan and communication
  foreign keys; the repair must remain test-only.
- Confirm independent complete coverage no longer reports either historical projection mismatch.
- Retain the original run's independently passed twice-run PostgreSQL acceptance evidence for the
  unchanged 010E2 implementation.

## Recommended Next Action
Run Ralph's complete independent repair validation and commit only if every gate passes.
