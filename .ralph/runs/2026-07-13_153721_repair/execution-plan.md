# Execution Plan

Selected slice: 007D3-returned-approval-cycle-and-resubmission-closure

## Repair Boundary

Preserve the complete quarantined 007D3 implementation. Repair only the demonstrated trusted
PostgreSQL acceptance mismatch: the protected validator selects three concurrency test classes and
requires exactly five discovered/passed races, while the current selection contains six after the
returned-cycle race was added.

## Steps

1. Reproduce the failure with the exact protected `postgresql_acceptance_log_passes` predicate and
   retain the red output in this repair run.
2. Inspect the sanction-submission concurrency class and split the legacy duplicate-submission
   regression from the validator-selected five-race class without weakening or deleting either
   test. Keep the 007D3 returned-cycle race in the selected class.
3. Run the exact five-race command with the mandated backend interpreter. If this sandbox denies
   PostgreSQL socket access, run deterministic collection plus focused SQLite/full-suite feedback
   and leave authoritative PostgreSQL execution to the orchestrator, as required by the slice.
4. Run proportional backend gates: focused tests, Django check, migration sync, and full coverage.
   No frontend source changed, but run the configured frontend build/typecheck/lint/test gates.
5. Save red/green evidence, changed-files, risk assessment, review packet, and final summary;
   refresh Ralph state/progress/handoff only as needed to describe this repair accurately. Confirm
   protected files are untouched and leave commit/merge/push to the orchestrator.

## Expected Proof

- The selected trusted command collects exactly five races, including
  `test_concurrent_returned_cycle_resubmissions_create_one_cycle_two_ledger`.
- The legacy duplicate-submission race remains independently discoverable and green in the full
  backend suite.
- Both orchestrator PostgreSQL repetitions can satisfy the exact five-test parser and proceed to
  record non-secret environment evidence.
