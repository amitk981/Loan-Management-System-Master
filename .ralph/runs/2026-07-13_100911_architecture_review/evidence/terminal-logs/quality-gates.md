# Quality Gates

## Frontend

Command sequence: `npm run build && npm run typecheck && npm run lint && npm test`

- Build: PASS; Vite transformed 1,871 modules and produced the bundle. The existing large-chunk
  warning remained non-failing.
- Typecheck: PASS (`tsc --noEmit`).
- Lint: PASS (`eslint src`).
- Tests: PASS; 29 files, 208 tests, 0 failures in 7.58 seconds.

## Backend

Every command used `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.

- `manage.py check`: PASS; no issues.
- `manage.py makemigrations --check --dry-run`: PASS; no changes detected.
- Full suite under coverage: PASS; 566 tests in 84.512 seconds, 16 expected PostgreSQL-only skips.
- Coverage: PASS; 20,809 statements, 1,502 missed, 93%, above the 85% floor.

The architecture review declared no PostgreSQL runtime capability. Its conclusions additionally
inspect the two retained PostgreSQL executions from 007A5; it does not fabricate a new socket gate.

