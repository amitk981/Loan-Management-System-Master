# Execution Plan

Selected slice: 010K3-servicing-as-of-owner-boundary-closure

## Demonstrated failure

Independent backend coverage failed only
`sfpcl_credit.tests.test_dpd_monitoring_api.DpdMonitoringApiTests.test_bounded_active_portfolio_reports_each_outcome`:
the bounded portfolio request executed 21 queries against an asserted ceiling of 20.

## Repair boundary

1. Preserve the existing 010K3 candidate and reproduce the exact named test with the mandated Ralph
   virtual-environment interpreter.
2. Inspect only the query-producing DPD monitoring path and its existing regression test. Rank and
   test likely causes without widening the servicing owner-boundary behavior.
3. Add or retain a red-capable regression assertion at the public API seam, then make the smallest
   production or test-fixture correction justified by the captured queries.
4. Rerun the exact validator until it passes, then run the directly impacted 010K3 tests and backend
   check/migration-sync gates appropriate to the changed domain. Do not run the complete backend suite
   or coverage locally.
5. Save repair evidence under this run directory, complete risk/review/final artifacts, and run
   exactly `./scripts/ralph-validate-review-closure.sh --slice docs/slices/010K3-servicing-as-of-owner-boundary-closure.md --run-dir .ralph/runs/2026-07-21_070957_repair` until PASS.

## Constraints

- No frontend, source-document, protected-file, queue-state, or unrelated servicing changes.
- No git add/commit/push; independent validation and commit remain orchestrator-owned.
- Preserve all original-run closure evidence and candidate behavior unless the demonstrated query
  regression proves a narrowly related defect.
