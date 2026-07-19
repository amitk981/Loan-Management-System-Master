# Repair Verification

## Tight Red/Green Loop

Command:

```text
/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test sfpcl_credit.tests.test_appraisal_api.AppraisalHistoryHardeningMigrationTests.test_forward_repair_requires_positive_exact_chronology_and_backfills_latest_only --verbosity 2
```

Before the repair it failed deterministically with:

```text
django.db.utils.IntegrityError: NOT NULL constraint failed: audit_logs.selector_manifest_json
Ran 1 test in 30.310s
FAILED (errors=1)
```

After the repair the same label passed:

```text
Ran 1 test in 40.303s
OK
```

## Expanded Checks

- The five exact test labels named in the failed coverage log: `Ran 5 tests in 155.223s` / `OK`.
- Owner-selector equivalence plus pgcrypto migration ownership: `Ran 13 tests in 2.783s` / `OK`.
- `manage.py makemigrations --check --dry-run`: `No changes detected`.
- `manage.py check`: `System check identified no issues (0 silenced)`.
- `git diff --check`: exit 0, no output.
- `[DEBUG-` instrumentation scan across affected backend modules: no matches.

Raw command output is retained beside this file under `terminal-logs/`.
