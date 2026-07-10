# Execution Plan

Selected slice: 006F4-postgresql-credit-concurrency-acceptance

## Repair Diagnosis

- The previous `2026-07-10_225141_normal_run` worktree remains orphaned and contains ungated
  changes; none will be salvaged.
- Its two independent PostgreSQL runs passed, but Ralph validation failed because the environment
  probe imported `sfpcl_credit.config.postgres_test_settings` from `sfpcl_credit/` without adding
  the repository root to `sys.path`, producing `ModuleNotFoundError: No module named
  'sfpcl_credit'` after the tests had passed.
- This repair will produce fresh red/green evidence and a self-contained non-secret environment
  record from the required interpreter and current worktree.

## Plan

1. Execute the exact five-test PostgreSQL command unchanged and save the full initial red output.
2. Repair one public-interface acceptance defect at a time: fixture binding, canonical workflow
   event assertions, then the application-row lock on PostgreSQL. Rerun the same command after
   each correction and retain every red/green transition.
3. Add a run-local fail-closed acceptance verifier test before its implementation. It must reject
   missing markers, skips, zero-test output, connection/setup failures, and failed output, and
   accept exactly two complete five-test logs.
4. Run the exact combined command twice after the corrections, record PostgreSQL server version and
   non-secret database/host/port facts, and run the verifier against both final logs.
5. Run all configured backend and frontend quality gates with the mandated interpreters/tooling.
6. Save changed-file, risk, review, and final evidence; update the selected slice, state, progress,
   handoff, and Epic 006 digest; sharpen the next two Not Started slices using already-opened
   requirements.

## Public Behaviors Preserved

- One application row serializes loan-limit, appraisal/rejection, and sanction mutations.
- Exactly one terminal winner and one complete evidence set persist; losers write no success facts.
- No formula, endpoint, permission, state-machine, schema, migration, or frontend behavior changes.
