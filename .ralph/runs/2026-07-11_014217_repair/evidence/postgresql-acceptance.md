# PostgreSQL Five-Race Acceptance

The exact 006F4 authoritative command was run twice after the approvals-module extraction:

```text
/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test sfpcl_credit.tests.test_credit_modules.LoanLimitConcurrencyTests sfpcl_credit.tests.test_appraisal_api.AppraisalConcurrencyTests sfpcl_credit.tests.test_sanction_submission_api.SanctionSubmissionConcurrencyTests --settings=sfpcl_credit.config.postgres_test_settings -v 2
```

Both `terminal-logs/postgresql-five-race-run-1.txt` and
`terminal-logs/postgresql-five-race-run-2.txt` report five found/executed tests, `OK`, and zero
skips. The sanction duplicate race still serializes through the application lock to one case and
one audit/workflow evidence set.

`terminal-logs/postgresql-environment.txt` records only non-secret facts: PostgreSQL 14.20,
database `sfpcl_credit`, test database `test_sfpcl_credit`, local socket, port 5432.
