# Focused GREEN — witness historical migration isolation

Command (from `sfpcl_credit/`):

```text
PYTHONEXECUTABLE=/Users/amitkallapa/LMS/.ralph/venv/bin/python /Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test sfpcl_credit.tests.test_witness_evidence_migration.WitnessEvidenceMigrationTests.test_backfill_is_idempotent_and_reverse_preserves_legacy_rows --verbosity 2
```

Result: `OK`, exit code `0`, 1 test run in 88.282 seconds.

The setup created legacy Witness rows against the pre-`applications.0012` physical schema, the
backfill remained idempotent, and reversing preserved all legacy rows.
