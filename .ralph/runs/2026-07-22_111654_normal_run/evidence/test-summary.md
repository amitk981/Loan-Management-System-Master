# Test Summary

## TDD evidence

- `red-01-grace-boundary.log` / `green-01-grace-boundary.log`: derived month-end boundary.
- `red-02-grace-cure.log` / `green-02-grace-cure.log`: canonical full-principal cure.
- `red-03-grace-expiry-task.log` / `green-03-grace-expiry-task.log`: leap-year expiry and retry-safe task.
- `red-04-assessment-api.log` / `green-04-assessment-api.log`: assessment persistence/API/projection.
- `red-07-processor-failure-count.log` / `green-07-processor-failure-count.log`: bounded failure rollback.
- `red-08-derived-cure.log` / `green-08-derived-cure.log`: immediate canonical cured projection.
- `red-10-scheduled-entrypoint.log` / `green-10-scheduled-entrypoint.log`: scheduled task entrypoint.

## Focused results

- `focused-final-regression.log`: 39 tests passed in 11.701s.
- `focused-available-action.log`: 1 test passed.
- `backend-check.log`: zero system-check issues.
- `migration-sync.log`: no model/migration drift.
- `migration-plan.log`: `defaults.0002_grace_period_assessment` is planned.
- `postgresql-acceptance-local-collection.log`: exactly one test collected and skipped because the
  local backend is SQLite; trusted PostgreSQL execution is not claimed.

The agent did not run the complete backend suite or coverage. Ralph owns the authoritative selected
backend lane and twice-run PostgreSQL acceptance.
