# Dashboard Query/Performance Evidence

- Test: `test_credit_dashboard_batches_card_counts_within_fixed_query_budget`
- Representative API: authenticated `GET /api/v1/dashboard/`
- Bound: at most 10 database queries for the ten-card Credit Manager catalogue.
- Result: PASS in `evidence/terminal-logs/backend-focused-final.log`.
- Count batching: application status counts share one aggregate, appraisal TAT/review counts share
  one aggregate, and scoped loan outstanding/DPD counts share one aggregate. No card serialises
  source rows or performs a query per result row.
- Unit CI deliberately does not assert the source `<3 seconds` wall-clock target. The focused
  dashboard module completed in under one second after database setup. The supported-role budget
  matrix separately caps CFO, Compliance, Treasury, Accounts, and CS at 24 queries so distinct
  owning-domain selectors remain scope-authoritative without query growth by result row. Trusted load
  validation remains responsible for the 50-user `PERF-002` workload.
