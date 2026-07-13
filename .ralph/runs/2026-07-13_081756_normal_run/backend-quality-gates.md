# Backend Quality Gates

Commands used `/Users/amitkallapa/LMS/.ralph/venv/bin/python` exclusively.

- `manage.py check`: passed, 0 issues.
- `manage.py makemigrations --check --dry-run`: passed, no changes detected.
- `coverage run --source=sfpcl_credit manage.py test sfpcl_credit.tests`: 535 tests passed
  in 75.967 seconds with 16 expected PostgreSQL-only skips.
- `coverage report --fail-under=85`: passed at 93% total coverage.
- `ApprovalMatrixConcurrencyTests` under
  `sfpcl_credit.config.postgres_test_settings`: four named races passed twice; the final run had no
  unapplied migrations. Logs `06`, `11`, and `12` retain exact names and output.
- Migration evidence: `10-migration-list.txt` shows proposal migration `0005` and case snapshot
  migration `0006`; `11-governed-races-green-2.txt` records PostgreSQL applying `0006` after `0005`.

Detailed coverage output is retained in `evidence/terminal-logs/13-backend-full-gates.txt`.
