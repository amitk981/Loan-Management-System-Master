# Repair Diagnosis Evidence

## Demonstrated failure

The independent run failed five tests across these exact classes:

- `sfpcl_credit.tests.test_credit_model_ownership_migration.CreditAssessmentModelOwnershipMigrationTests`
- `sfpcl_credit.tests.test_witness_evidence_migration.WitnessEvidenceMigrationTests`

The focused command reproduced all five errors with exit code 1. The retained RED output is
`terminal-logs/migration-regression-red.log`.

## Root cause

Both historical migration tests construct a projected app registry from the migration graph's leaf
nodes after rolling the physical database back to an old `applications` schema. Slice 010E2 adds
`configurations.0006`, a legitimate graph leaf whose foreign-key dependencies transitively require
current `loans`, `applications`, and `credit` migrations. The tests did not exclude the
`configurations` owner, so their projected historical models included current credit ownership and
current witness fields while the corresponding database tables remained rolled back.

This mismatch caused:

- `LookupError` for `applications.EligibilityAssessment`, because the projected state had already
  moved it to `credit`; and
- `OperationalError` for `witnesses.verification_folio_number`, because the projected model had the
  field while the rolled-back table did not.

The new migration does not mutate either legacy table. The repair adds `configurations` to the two
tests' existing downstream-owner exclusion sets so their in-memory model states match the schemas
they deliberately exercise.

## Verification

- Focused migration regressions: 5 passed, exit code 0 —
  `terminal-logs/migration-regression-green.log`.
- Slice 010E2 focused API/service tests: 8 run, 5 passed and 3 PostgreSQL-only skips, exit code 0 —
  `terminal-logs/interest-rate-focused-green.log`.
- Django system check: passed, exit code 0 — `terminal-logs/backend-check-green.log`.
- Migration synchronization: no changes detected, exit code 0 —
  `terminal-logs/migration-sync-green.log`.

The authoritative complete backend coverage suite is intentionally reserved for Ralph's independent
repair validation.
