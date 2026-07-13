# Quality Gate Results

All commands used the active worktree. Backend commands used exactly
`/Users/amitkallapa/LMS/.ralph/venv/bin/python`.

- Frontend `npm run build`: PASS; 1,871 modules transformed. Existing large-chunk warning only.
- Frontend `npm run typecheck`: PASS.
- Frontend `npm run lint`: PASS.
- Frontend `npm test`: PASS; 29 files, 208 tests.
- Backend `manage.py check`: PASS; no issues.
- Backend `manage.py makemigrations --check --dry-run`: PASS; no changes detected.
- Backend coverage test run: PASS; 677 tests, 19 expected PostgreSQL-only SQLite skips.
- Backend `coverage report --fail-under=85`: PASS; 93% total coverage.

The two deliberately failing diagnostic probes are recorded separately in
`frozen-provenance-probes.log`; they reproduce the review finding and are not configured gates.
