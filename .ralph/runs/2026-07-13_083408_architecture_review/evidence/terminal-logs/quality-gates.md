# Quality Gates

## Frontend

Command sequence: `npm run build && npm run typecheck && npm run lint && npm test`

- Build: PASS; Vite transformed 1,871 modules and produced the bundle. Existing large-chunk warning
  remained non-failing.
- Typecheck: PASS (`tsc --noEmit`).
- Lint: PASS (`eslint src`).
- Tests: PASS; 29 files, 208 tests, 0 failures, 7.02 seconds.
- The affected member-governance container file passed all 16 tests; routed create took 1,359 ms.

## Backend

All commands used `/Users/amitkallapa/LMS/.ralph/venv/bin/python` as required.

- `manage.py check`: PASS, no issues.
- `manage.py makemigrations --check --dry-run`: PASS, no changes detected.
- Full suite under coverage: PASS; 535 tests in 75.168 seconds, 16 expected PostgreSQL-only skips.
- Coverage: PASS; 19,952 statements, 1,378 missed, 93%, above the 85% floor.

