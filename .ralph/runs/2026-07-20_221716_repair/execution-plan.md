# Execution Plan

Selected slice: CR-014-rate-current-date-terminal-finalizer
Mode: same-worktree repair

1. Preserve the quarantined candidate and reproduce the exact trusted PostgreSQL failure from the
   prior run: `RateCurrentDateFinalizerPostgreSQLAcceptanceTests`, expected count 5.
2. Minimise the failing competing-portfolio scenario and inspect only the current-rate owner and
   Loan Account collection boundary implicated by its `total_count` mismatch.
3. Add or strengthen a RED regression only if the existing five-test contract does not isolate the
   demonstrated defect; otherwise retain the existing failing acceptance test as the RED loop.
4. Apply the smallest correction in the demonstrated PostgreSQL/current-rate projection domain,
   preserving server-date ownership, account scope, replay, and concurrency guarantees.
5. Rerun the exact named PostgreSQL validator until all five tests pass, twice where the slice
   contract requires it; save repair evidence under this run's `evidence/terminal-logs/`.
6. Run focused reverse-consumer, system-check, and migration-sync checks proportional to the edit.
7. Complete the risk assessment, review packet, final summary, and machine-readable review-closure
   contract. Do not alter orchestrator-owned state, slice status, or changed-files bookkeeping.
