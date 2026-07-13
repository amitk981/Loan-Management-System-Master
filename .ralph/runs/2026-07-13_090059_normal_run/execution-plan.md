# Execution Plan

Selected slice: `007A5-approval-governance-complete-loser-ledger`

1. Extend the existing PostgreSQL `ApprovalMatrixConcurrencyTests` through public/module boundaries
   with a discriminating open approval-case fixture and a complete configuration ledger snapshot.
2. RED: require every governed rule/committee create/supersede race to prove exact winner-only
   changes, a byte-for-byte pending loser, public proposal-detail readback, and immutable case state.
3. GREEN: make the smallest production correction only if the new behavioral proof exposes a real
   defect; keep all activation behind `decide_proposal` and the configuration lock.
4. Add independently named committee historical/current resolver and conflicting-backfill public
   rows, plus independently attributable malformed/authority rows where the current suite compresses
   them. Save focused RED/GREEN logs and coverage evidence.
5. Run the four exact PostgreSQL race methods twice with migrations 0005 and 0006 visible, then run
   backend check, migration sync, full coverage, and all frontend gates required by Ralph.
6. Save changed-file, risk, review, and final-summary artifacts; update the epic digest, run-ahead
   sharpen the next one or two Not Started slices from already-opened material, then update slice,
   state, progress, and handoff status only after all gates pass.

Permissions check: intended edits are limited to `sfpcl_credit/**`, `docs/working/**`,
`docs/slices/**`, `.ralph/state.json`, `.ralph/progress.md`, and this run folder; all are listed as
allowed without approval. Protected and forbidden paths will remain unchanged.
