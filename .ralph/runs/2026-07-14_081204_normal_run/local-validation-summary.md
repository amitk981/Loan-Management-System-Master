# Local Validation Summary

- PASS: frontend build, typecheck, ESLint, and 287 tests.
- PASS: Django system check and migration drift check.
- PASS: 710 backend tests with 21 expected skips; 93% coverage against 85% floor.
- PASS: 39 focused documents/catalogue tests.
- PASS: both PostgreSQL template races twice against fresh databases/migrations.
- PASS: slice queue lint; the pending dependency graph drains.
- PASS: JSON state parses and `git diff --check` is clean.
- PASS: no protected path or `docs/source/` change.
- PASS: 15 product/documentation files and 707 changed lines excluding Ralph
  bookkeeping, below limits of 30 files and 2,000 lines.
- PASS: one migration and zero new dependencies, within configured limits.
