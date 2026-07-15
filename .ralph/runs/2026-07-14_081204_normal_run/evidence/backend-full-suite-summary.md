# Backend Full-Suite Summary

- Command: `/Users/amitkallapa/LMS/.ralph/venv/bin/python -m coverage run --source=sfpcl_credit manage.py test sfpcl_credit.tests`
- Result: PASS — 710 tests in 167.179 seconds; 21 expected PostgreSQL-only skips.
- Coverage command: `/Users/amitkallapa/LMS/.ralph/venv/bin/python -m coverage report --fail-under=85`
- Result: PASS — 93% total coverage against the 85% floor.
- The final full test and coverage outputs are in `terminal-logs/backend-full-tests-final.log` and
  `terminal-logs/backend-coverage-final.log`.
- Django system check and migration-drift output are in `terminal-logs/backend-check-final.log` and
  `terminal-logs/migration-sync-final.log`.

The authoritative PostgreSQL race suite is separate from the routine SQLite full suite. Both
template races passed twice against freshly created databases (including the final identity
migration) in `template-postgresql-fresh-migration-green-1.log` and
`template-postgresql-fresh-migration-green-2.log`.
