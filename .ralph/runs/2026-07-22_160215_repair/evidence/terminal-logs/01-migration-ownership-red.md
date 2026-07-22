# Focused RED — historical credit ownership migration

Command (from `sfpcl_credit/`):

```text
/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test sfpcl_credit.tests.test_credit_model_ownership_migration.CreditAssessmentModelOwnershipMigrationTests --verbosity 2
```

Result: `FAILED (errors=2)`, exit code `1`, 2 tests run in 69.455 seconds.

Exact failing signal in both tests:

```text
LookupError: App 'applications' doesn't have a 'EligibilityAssessment' model.
```

The failure occurs in `_create_pre_move_rows(old_apps)` after the test migrates to
`applications.0010_loanapplication_nominee` with `credit` absent, matching the authoritative backend
coverage failure.
