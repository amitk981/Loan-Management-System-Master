# Evidence Index

- `01-red-missing-dispatcher-send.log` / `02-green-dispatcher-send-interface.log`
- `03-red-generic-idempotency.log` / `04-green-generic-idempotency.log`
- `05-red-advice-idempotency.log` / `06-green-advice-idempotency.log`
- `08-red-import-cycle.log` / `09-green-import-cycle.log`
- `23-focused-after-provider-evidence.log`: 57 final focused tests.
- `27-final-persistence-regressions.log`: 11 adapter/persistence/H6 migration tests.
- `24-postgresql-final-run-1.log` and `25-postgresql-final-run-2.log`: all six five-caller
  races green in both executions.
- `28-backend-static-gates.log`: Django check and migration sync; compileall ran in the same gate.
- `29-final-audit.log`: JSON, diff, protected-path, backend check, migration-sync, and status audit.
- `26-frontend-gates.log`: frontend production build; typecheck/lint/331-test output is retained in
  the run transcript and summarized in the review packet.
