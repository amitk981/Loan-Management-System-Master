# PostgreSQL Credit Concurrency Acceptance

## Environment

- Engine: `django.db.backends.postgresql`
- PostgreSQL server: `14.20 (Homebrew)`
- Host: local Unix socket
- Port: `5432`
- Configured application database: `sfpcl_credit`
- Django test database: `test_sfpcl_credit`
- Credentials: intentionally omitted

## Authoritative Command

Run from `sfpcl_credit/` with the mandated interpreter:

```text
/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test sfpcl_credit.tests.test_credit_modules.LoanLimitConcurrencyTests sfpcl_credit.tests.test_appraisal_api.AppraisalConcurrencyTests sfpcl_credit.tests.test_sanction_submission_api.SanctionSubmissionConcurrencyTests --settings=sfpcl_credit.config.postgres_test_settings -v 2
```

## Result

Both final outputs contain `Found 5 test(s).`, `Ran 5 tests`, and `OK`, with no skipped, setup,
connection, or failure marker:

- `terminal-logs/postgresql-concurrency-green-1.log`
- `terminal-logs/postgresql-concurrency-green-2.log`

The two loan-limit, two appraisal/rejection, and one sanction-submission races preserved the
documented application-first order. The fail-closed verifier independently accepted exactly those
two files; see `terminal-logs/postgresql-acceptance-evidence-verification.log`.

## Red/Green Trail

- `terminal-logs/postgresql-concurrency-initial-red.log`: five fixture-binding/constraint errors.
- `terminal-logs/postgresql-after-fixture-binding.log`: sanction green; workflow/lock errors remain.
- `terminal-logs/postgresql-after-workflow-contract.log`: appraisal and sanction green; loan-limit
  setup exposes the real nullable-join row-lock error.
- `terminal-logs/postgresql-concurrency-green-1.log`: all five green after the base-row lock fix.
- `terminal-logs/postgresql-concurrency-green-2.log`: repeat all-five green acceptance.
