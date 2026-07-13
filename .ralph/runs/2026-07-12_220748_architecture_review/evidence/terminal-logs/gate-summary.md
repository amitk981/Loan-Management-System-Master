# Gate Summary

Commands used the active worktree and the required backend interpreter
`/Users/amitkallapa/LMS/.ralph/venv/bin/python`.

- Frontend `npm run build`: PASS; Vite built 1,871 modules.
- Frontend `npm run typecheck`: PASS.
- Frontend `npm run lint`: PASS.
- Frontend `npm test -- --run`: PASS; 29 files, 199 tests.
- Backend `manage.py check`: PASS; no issues.
- Backend `manage.py makemigrations --check --dry-run`: PASS; no changes detected.
- Backend coverage test run: PASS; 460 tests, 8 expected SQLite skips.
- Backend coverage report: PASS; 93%, floor 85%.
- Ralph slice queue lint: PASS; no output/problems.
- Ralph workflow regressions: PASS.
- `git diff --check`: PASS.
- Production-code unchanged check: PASS; no files under `sfpcl_credit/` or `sfpcl-lms/` changed.

