# Quality Gates

- `npm run typecheck`: PASS.
- `npm run lint`: PASS.
- `npm run build`: PASS, 1,871 modules transformed.
- `npm test`: PASS on isolated full-suite rerun, 29 files and 204 tests. An earlier concurrent run
  timed out one unrelated five-second demo-auth case; the complete isolated rerun passed it.
- `/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py check`: PASS, zero issues.
- `/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py makemigrations --check --dry-run`: PASS,
  no changes detected.
- Coverage suite: PASS, 494 tests in 54.889 seconds, 12 expected skips.
- Coverage report: PASS, 93% total against the 85% floor.
- `git diff --check`: PASS.
