# Quality Gate Evidence

- `npm run typecheck`: PASS
- `npm run lint`: PASS
- `npm test -- --run`: PASS — 18 files, 126 tests
- `npm run build`: PASS — 1,871 modules transformed
- `/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py check`: PASS
- `/Users/amitkallapa/LMS/.ralph/venv/bin/python sfpcl_credit/manage.py makemigrations --check --dry-run`: PASS — no changes
- `/Users/amitkallapa/LMS/.ralph/venv/bin/python -m coverage run --source=sfpcl_credit sfpcl_credit/manage.py test sfpcl_credit.tests`: PASS — 372 tests, 5 PostgreSQL-only skips
- `/Users/amitkallapa/LMS/.ralph/venv/bin/python -m coverage report --fail-under=85`: PASS — 93%
- `git diff --check`: PASS
- Validator line calculation: 1,978 of 2,000 lines; 17 files of 30.
