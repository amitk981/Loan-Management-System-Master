# Repair Failure Diagnosis

## Failed Run Inspected

`2026-07-10_225141_normal_run` remained as an orphaned worktree with ungated changes. Its product
tests, two PostgreSQL repetitions, coverage, and frontend gates were green, but Ralph validation
reported one failure:

`FAIL: PostgreSQL environment evidence is missing.`

The independent environment probe failed after the test runs for two reasons:

1. It changed into `sfpcl_credit/` and directly imported
   `sfpcl_credit.config.postgres_test_settings` without `manage.py` adding the repository root to
   `sys.path`, producing `ModuleNotFoundError: No module named 'sfpcl_credit'`.
2. When reproduced from the correct import root, the probe attempted to connect to configured
   application database `sfpcl_credit`. This acceptance setup creates only temporary
   `test_sfpcl_credit`; the persistent application database is intentionally absent.

The repair did not salvage the orphaned diff. It rebuilt each change after a fresh red run and
queried server version through PostgreSQL's `postgres` maintenance database while separately
recording the configured application/test names. No protected validator script was modified.

## Fresh Red Feedback Loop

The exact five-test command found and ran all five tests. It failed with four inherited static
fixture-binding errors and one PostgreSQL `varchar(80)` error caused by the same binding issue. The
next run exposed two retired workflow-event queries plus two real nullable-outer-join `FOR UPDATE`
errors. Each narrowing run is retained under `terminal-logs/`.
