# 011D PostgreSQL Acceptance Repair Evidence

## Exact validator

```text
SFPCL_POSTGRES_TEST_DB=<isolated-name> /Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test sfpcl_credit.tests.test_default_recovery_postgresql_acceptance.NonPaymentNotePostgreSQLAcceptanceTests --settings=sfpcl_credit.config.postgres_test_settings --noinput -v 2
```

Expected and final discovered count: 2 tests.

## Red and progressive diagnosis

- The two independent prior-run logs, `postgresql-acceptance-validation-1.txt` and
  `postgresql-acceptance-validation-2.txt`, both failed with `FOR UPDATE cannot be applied to the
  nullable side of an outer join` at the create locking query.
- `postgresql-acceptance-repair-1.log` proved the create correction and exposed the same outer-join
  lock error in submit: one test passed, one errored.
- `postgresql-acceptance-repair-2.log` proved that removing the eager joins cleared both failures,
  but targeted review rejected that intermediate shape because it also stopped locking the
  canonical loan balance row.
- `postgresql-acceptance-repair-3-final.log` tested explicit lock targets while still eager-loading
  nullable relations. It exposed a stale cached `approval_case=None` on concurrent replay.

## Final green

- `postgresql-acceptance-repair-4-final.log`: PostgreSQL created an isolated database, found exactly
  2 tests, both five-worker convergence tests passed, `Ran 2 tests`, `OK`, exit code 0.
- `postgresql-environment.log`: `vendor=postgresql`, `pg_version=140020`, exit code 0.
- `focused-repair-checks.log`: 6 Non-Payment Note workflow tests passed; Django system check passed;
  `makemigrations --check --dry-run` reported no changes; exit code 0.

## Final repair

The locking queries now use explicit PostgreSQL `FOR UPDATE OF` targets for the owning workflow row
and canonical loan row. Nullable assessment, extension, and approval relations are not joined into
the locking query, preventing PostgreSQL outer-join rejection and stale nullable relation caches
without weakening financial-row serialization.
