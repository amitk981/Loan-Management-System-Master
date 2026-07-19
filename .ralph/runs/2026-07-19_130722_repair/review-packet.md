# Review Packet: 2026-07-19_130722_repair

## Result
Ready for independent validation

## Slice
009L5-epic-009-exact-selector-and-consumer-parity-closure

## Recommended Next Action
Run Ralph's complete independent backend coverage and migration gates against the preserved 009L5
candidate; commit only if all validation passes.

## Repair Outcome

- Root cause: Django's PostgreSQL-only `CryptoExtension` operation was placed in a migration that
  the repository's historical migration tests also reverse on SQLite. Its reverse implementation
  queried `pg_extension`, which SQLite does not have.
- Fix: the migration now creates/drops `pgcrypto` only when the schema editor is connected to
  PostgreSQL and is a no-op on SQLite/other vendors.
- Scope: only `disbursements/migrations/0010_enable_pgcrypto_for_exact_selector.py` changed during
  repair. No existing selector, consumer, API, test, contract, frontend, or protected file was
  altered.

## Feedback Loop and Evidence

- `evidence/terminal-logs/pgcrypto-sqlite-red.log`: exact historical migration regression failed
  with `django.db.utils.OperationalError: no such table: pg_extension`.
- `evidence/terminal-logs/pgcrypto-sqlite-green.log`: the same test passed after the vendor guard.
- `evidence/terminal-logs/historical-migration-regressions-green.log`: all 19 tests in the classes
  responsible for the independent gate's 18 errors passed in 665.905 seconds.
- `evidence/terminal-logs/focused-selector-and-django-gates-green.log`: all 45 focused 009L5 tests
  passed; Django check and `makemigrations --check --dry-run` were green.

All evidence paths are relative to this repair run directory.

## Independent Review Notes

- The existing historical migration test is the correct regression seam: it exercises the actual
  full-schema rollback path that failed in coverage, so no narrower mock-only test was substituted.
- Reversible PostgreSQL extension behavior is preserved with explicit static SQL. Non-PostgreSQL
  behavior is intentionally empty because `pgcrypto` and `pg_extension` are PostgreSQL facilities.
- `git diff --check` passed. The complete backend suite and coverage were not rerun by the agent;
  Ralph owns that authoritative repair gate.

## Traceability

- Slice 009L5 requires the exact selectors to remain database-backed and the original packet records
  `pgcrypto` as their PostgreSQL SHA-256 prerequisite. This repair keeps that prerequisite on
  PostgreSQL while restoring repository-wide historical migration compatibility on SQLite.
- The repair does not change any M07/M08 business decision, authority, pagination, disclosure, or
  consumer edge implemented by the quarantined candidate.
