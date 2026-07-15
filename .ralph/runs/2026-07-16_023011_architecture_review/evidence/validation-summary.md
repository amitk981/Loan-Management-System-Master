# Validation Summary

All commands ran from the active architecture-review worktree on 2026-07-16.

## Review metadata

- Slice queue lint: passed.
- Capability declarations for 008L5 and 008M2: passed.
- `.ralph/state.json`: valid JSON.
- `git diff --check`: passed.
- Protected-path diff scan: empty.
- Blocked slices: zero.

## Frontend

Working directory: `sfpcl-lms`

- `npm run build`: passed; 1,879 modules transformed. Vite retained its existing large-chunk
  advisory warning.
- `npm run typecheck`: passed.
- `npm run lint`: passed.
- `npm test`: passed; 36 files and 311 tests.

## Backend

Working directory: `sfpcl_credit`

Every command used `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.

- `manage.py check`: passed, no issues.
- `manage.py makemigrations --check --dry-run`: passed, no changes detected.
- Coverage test run: passed; 905 tests in 333.741 seconds, 46 skipped.
- Coverage report: 91% total across 37,315 statements, above the required 85% threshold.

## Focused review probes

Both intentionally failing probes reproduced review findings. Their assertions and observed values
are recorded in `terminal-logs/review-probes.md`; they are not quality-gate failures because the
architecture-review mode forbids production fixes and queues corrective slices instead.
