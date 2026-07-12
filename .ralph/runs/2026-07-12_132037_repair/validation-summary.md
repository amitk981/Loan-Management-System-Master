# Validation Summary

## Exact Repair Feedback Loop

- Red: the protected predicate rejected the preserved green six-test log because it requires
  exactly `Found 5` and `Ran 5`.
- Green: two fresh PostgreSQL logs each report `Found 5 test(s).`, `Ran 5 tests`, `OK`, and no
  skips; the protected predicate accepts both.

## Configured Gates

- Frontend build: PASS
- Frontend typecheck: PASS
- Frontend lint: PASS
- Frontend tests: PASS — 27 files, 173 tests
- Django check: PASS — no issues
- Migration sync: PASS — no changes detected
- Backend coverage suite: PASS — 433 tests, 5 expected SQLite-only skips
- Coverage floor: PASS — 94% against 85% required
- PostgreSQL acceptance: PASS twice — 5 tests per run, zero skips
- PostgreSQL environment probe: PASS — PostgreSQL 14.20, credentials omitted
- Diff whitespace check: PASS
- Protected-path scan: PASS

Detailed command output is stored in `evidence/terminal-logs/`.
