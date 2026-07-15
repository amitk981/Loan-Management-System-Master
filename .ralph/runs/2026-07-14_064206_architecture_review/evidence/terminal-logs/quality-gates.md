# Quality Gate Evidence

All commands used the active worktree. Backend commands used exactly
`/Users/amitkallapa/LMS/.ralph/venv/bin/python`.

## Frontend

- `npm run build`: PASS — Vite 5.4.21, 1,877 modules transformed. Existing >500 kB chunk warning
  only; build completed successfully.
- `npm run typecheck`: PASS — `tsc --noEmit`.
- `npm run lint`: PASS — `eslint src`.
- `npm test -- --run`: PASS — 33 files, 269 tests.

## Backend

- `.../python sfpcl_credit/manage.py check`: PASS — no issues.
- `.../python sfpcl_credit/manage.py makemigrations --check --dry-run`: PASS — no changes detected.
- `.../python -m coverage run --source=sfpcl_credit sfpcl_credit/manage.py test sfpcl_credit.tests`:
  PASS — 700 tests in 168.698 seconds, 20 expected skips.
- `.../python -m coverage report --fail-under=85`: PASS — 93% total coverage (25,889 statements,
  1,819 missed), above the 85% floor.

No production, browser spec, or PostgreSQL acceptance behavior changed in this architecture-review
run. The selected descriptor declares no special runtime capability, so retained two-run browser
and PostgreSQL evidence was inspected and no screenshot or acceptance result was fabricated.

