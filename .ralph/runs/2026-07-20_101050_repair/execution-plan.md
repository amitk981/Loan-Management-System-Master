# Execution Plan

Selected slice: 010H-interest-capitalisation-after-30-april

## Repair boundary

Preserve the quarantined 010H implementation and fix only the independently demonstrated
PostgreSQL acceptance failure. The failing lock query must continue to lock the current eligible
invoice rows while avoiding a PostgreSQL `FOR UPDATE` request against the nullable reverse
capitalisation-evidence join. No new product behavior, schema, API, frontend, or business rule is
in scope.

## Feedback loop and TDD evidence

1. Retain the two failed authoritative PostgreSQL logs from the normal run as RED evidence; both
   execute the exact declared one-test contract and fail with the same database error.
2. Apply the smallest query-lock correction and run the exact declared test with the mandated
   Ralph Python interpreter and PostgreSQL settings. Save the result as repair GREEN evidence.
3. Run the focused interest-capitalisation API tests plus Django check and migration-sync to prove
   the backend-neutral behavior remains intact. Do not run the complete backend suite or coverage.
4. Confirm no debug instrumentation or protected-path changes, then complete the repair risk,
   review, and final-summary artifacts for independent validation.
