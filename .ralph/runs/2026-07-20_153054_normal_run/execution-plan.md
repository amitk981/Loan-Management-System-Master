# Execution Plan

Selected slice: 010I-dpd-calculation-and-monitoring-buckets

1. Add a focused monitoring owner with an immutable DPD snapshot, an optional effective operational-bucket scheme, a database uniqueness rule for `(loan account, as-of date)`, and a loan current-snapshot pointer update. Keep default/reminder/workflow state outside the module.
2. Drive implementation through public API tracer bullets: RED/GREEN for a current/overdue calculation first, then the calendar and payment-timing matrix, stable replay/history, strict read/calculate permissions and account scope, and bounded portfolio outcomes/query behavior.
3. Add the declared PostgreSQL same-loan/date contention acceptance test and retain one snapshot/current pointer under concurrent calculation.
4. Update the monitoring API contract, run focused monitoring tests plus the 010A/010C/010H reverse-consumer labels, then run backend check and migration-sync without running the complete backend suite.
5. Save red/green, focused, reverse-consumer, check, migration, and PostgreSQL collection evidence; complete the risk assessment, review packet, and final summary with source-to-test traceability.

Permission check: planned changes are limited to `sfpcl_credit/**`, `docs/working/**`, and this run's `.ralph/runs/**`, all allowed by `.ralph/permissions.json`. Protected and forbidden paths remain untouched.
