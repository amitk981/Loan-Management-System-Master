# Risk Assessment

Risk level: High (inherited 009H4 slice); Low incremental repair risk

- Selected slice: 009H4-communications-advice-evidence-and-legacy-replay-closure
- Mode: repair
- Manual review required: yes; independent Ralph validation is required before commit.

## Demonstrated failure and repair scope

- Complete parallel coverage ran the receipt-owner migration test after an older approval migration
  boundary. SQLite rebuilt the receipt table during reverse migration with the same columns and
  constraints in a different ordinal order, so an order-sensitive legacy assertion failed.
- The repair changes one test expression only: the receipt column names are sorted before comparison.
  The detailed 009H4 manifest still proves exact type, null, default, FK, unique, check, index,
  definition, table, and row truth independently.
- No production model, service, migration operation, API, frontend, provider, dependency, source
  document, or financial behavior changed during repair.

## Underlying slice risk retained

- 009H4 remains High risk because it changes retained communications/provider evidence, legacy data
  backfill and reversal, protected terminal delivery truth, and PostgreSQL concurrency behavior.
- Complete backend coverage and the declared PostgreSQL acceptance gate remain mandatory independent
  checks even though this repair does not touch those production paths.

## Residual risk

- The validator-compatible historical sequence and 40 focused tests prove the assertion is now
  migration-order independent. Only Ralph's full parallel coverage rerun can prove there is no
  unrelated downstream failure in the complete suite.
- A local parallel supplemental run was excluded because spawned workers loaded an x86_64 process
  against the arm64 CFFI extension. Serial focused evidence uses the mandated Ralph interpreter and
  matches the original failure sequence exactly.
