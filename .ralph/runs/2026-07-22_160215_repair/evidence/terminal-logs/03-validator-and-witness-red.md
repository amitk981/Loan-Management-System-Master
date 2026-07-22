# Newly exposed migration-isolation RED

## Exact validator rerun

The six-worker backend coverage validator advanced beyond the original credit migration failure and
then stopped under failfast with:

```text
ERROR: test_backfill_is_idempotent_and_reverse_preserves_legacy_rows
django.db.utils.OperationalError: table witnesses has no column named verification_folio_number
Ran 1607 tests in 1103.755s
FAILED (errors=1, skipped=160)
Exit code: 1
```

The first validator invocation from Codex also exposed a Rosetta-only worker launch mismatch. The
approved venv wrapper starts the parent as ARM64, but multiprocessing used the underlying universal
`python3.11` as x86_64. Setting `PYTHONEXECUTABLE` to the same approved wrapper made both a probe
parent and child ARM64 and allowed `_cffi_backend` to import. No repository or dependency change was
made for that operator-environment correction.

## Tight focused reproducer

Command (from `sfpcl_credit/`):

```text
PYTHONEXECUTABLE=/Users/amitkallapa/LMS/.ralph/venv/bin/python /Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py test sfpcl_credit.tests.test_witness_evidence_migration.WitnessEvidenceMigrationTests.test_backfill_is_idempotent_and_reverse_preserves_legacy_rows --verbosity 2
```

Result: `FAILED (errors=1)`, exit code `1`, 1 test run in 56.882 seconds, with the same missing
physical-column signal.

Cause: the new downstream `recovery` leaf was included in a pre-`applications.0012` state
projection. Its dependencies pulled the later Witness model into the historical app registry while
the database had correctly migrated back to the older table schema.
