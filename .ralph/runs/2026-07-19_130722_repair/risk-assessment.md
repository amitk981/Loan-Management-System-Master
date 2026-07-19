# Risk Assessment

Risk level: High (inherited from slice 009L5); repair delta is narrow.

- Selected slice: 009L5-epic-009-exact-selector-and-consumer-parity-closure
- Mode: repair
- Demonstrated failure: the new `CryptoExtension` operation queried PostgreSQL's `pg_extension`
  table while historical migrations were reversed on SQLite, causing all 18 independent errors.
- Repair: replace that operation with reversible `CREATE EXTENSION IF NOT EXISTS pgcrypto` / `DROP
  EXTENSION IF EXISTS pgcrypto` SQL guarded by `connection.vendor == "postgresql"`; SQLite and
  other non-PostgreSQL databases perform no extension operation.
- Blast radius: one uncommitted migration file. The quarantined 009L5 selector, consumer, API,
  tests, and contract changes were preserved unchanged by the repair.
- Data-integrity assessment: no model state or data migration changed. PostgreSQL receives the same
  intended extension lifecycle; SQLite no longer executes PostgreSQL catalogue queries.
- Verification: the exact failing regression changed RED to GREEN; all 19 migration regressions
  covering the 18 independent errors passed; all 45 focused 009L5 tests, Django check, migration
  sync, and `git diff --check` passed.
- Residual risk: local evidence cannot prove PostgreSQL deployment privileges to create `pgcrypto`.
  This is unchanged from the original extension operation and must remain subject to Ralph's
  independent database/migration validation and deployment policy.
- Protected/source paths: none modified by this repair.
- Manual review required: yes, through Ralph's independent full-suite and coverage validation.
