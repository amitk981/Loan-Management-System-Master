# Execution Plan

Selected slice: 010N-global-search-api-and-ui

Repair scope: the independent complete-backend validator failed only in
`AppraisalHistoryHardeningMigrationTests.test_forward_repair_requires_positive_exact_chronology_and_backfills_latest_only`
because an older historical `Member` model could not insert through the new `members.aadhaar_last4`
database constraint.

1. Reproduce the exact failing test with the mandated backend interpreter and save the RED output.
2. Inspect the historical model state and live test schema to prove whether the new column lacks a
   compatibility default for cross-app migration tests.
3. Add a regression assertion at the migration seam, then make the smallest members migration/model
   correction that preserves indexed suffix search and permits older historical models to insert.
4. Rerun the exact failing selector to GREEN, then run the directly impacted global-search and
   members reverse-consumer tests plus Django check and migration-sync check.
5. Save repair evidence, risk assessment, final summary, and a review packet whose result is exactly
   `Ready for independent validation`; leave full-suite coverage to the orchestrator.
