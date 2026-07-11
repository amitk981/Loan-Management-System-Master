# Validation Results

- TDD RED: expected failure captured; the former collector did not resolve a package-level
  `from sfpcl_credit import approvals` edge.
- TDD GREEN: 3 dependency resolver/guard/repository tests passed.
- Focused sanction suite: 12 passed, 1 expected PostgreSQL-only skip under SQLite.
- Frontend lint: passed.
- Frontend typecheck: passed.
- Frontend build: passed (existing Vite chunk-size warning only).
- Frontend tests: 144 passed across 23 files.
- Django system check: passed.
- Migration drift check: no changes detected.
- Backend full suite: 396 passed, 5 expected skips.
- Backend coverage: 94%, above the 85% floor.
