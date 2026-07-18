# Evidence — 009H8 Communications Worker Runtime

No real external provider or network transport was invoked. Eager integrations use the deterministic
Fake adapter; PostgreSQL tests use the same adapter and retained idempotency identity.

## Test-first evidence

- `terminal-logs/red-worker-runtime.txt` records the missing Celery app, absent commit enqueue,
  missing lease/fencing/evidence interfaces, broker-publish crash, and advice-claim fence failures.
- `terminal-logs/green-worker-runtime.txt` and `terminal-logs/focused-worker-final.txt` record the
  focused runtime/dispatcher/API/migration suite after implementation.

## Concurrency evidence

- `terminal-logs/postgresql-worker-races-run-1.txt` records the first genuine PostgreSQL failure:
  `FOR UPDATE` attempted to lock a nullable outer-join side.
- `terminal-logs/postgresql-worker-races-fix.txt` records the row-targeted lock correction.
- `terminal-logs/postgresql-worker-races-postfence-fix.txt` and
  `terminal-logs/postgresql-worker-races-postfence-2.txt` are the two final green executions of all
  10 five-caller queue, five-worker claim, and stale-recovery races.

## Gates

- `terminal-logs/backend-static-final.txt`: Django check, migration sync, compilation, state JSON,
  and diff whitespace.
- `terminal-logs/frontend-typecheck.txt`, `frontend-lint.txt`, `frontend-tests.txt`, and
  `frontend-build.txt`: unchanged frontend gates; 38 files and 331 tests pass.
- Complete backend coverage is intentionally delegated to the Ralph orchestrator.
