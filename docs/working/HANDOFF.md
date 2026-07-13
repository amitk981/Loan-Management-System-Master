# Ralph Handoff

## Last Run

2026-07-14_013505_normal_run

## Current Status

`007K-frozen-review-snapshot-and-selector-boundary-closure` is complete. Credit owns the locked
review-package projection; approvals stores it unchanged and requires its complete typed schema,
persisted immutable review link, exact reviewer/provenance identity, typed nested identifiers and
timestamps, exact application references, and amount/provenance consistency.
Missing or malformed review truth now fails closed across collection, detail, actions, sanction
decision, Exception Register, and Credit Sanction Register before counts or writes, even with stale
true coherence/read projections.

The selector again owns query shaping only. One approval-engine read decision owns frozen validity
plus actor scope for every case/decision/register consumer. Live appraisal/application/risk changes
do not alter pending or terminal detail/history/decision/register output, and returned/corrected
cycle snapshots remain distinct. New packages carry credit schema/review-decision provenance;
legacy 0011/0012 mutable-row reconstructions lack that proof and remain hidden. No migration was
added and the worktree has no migrated retained application database; no unproven backfill ran.

## Validation

Backend RED/GREEN and review-fix evidence is retained in
`.ralph/runs/2026-07-14_013505_normal_run/evidence/terminal-logs/`. Django check and migration sync
pass; all 685 backend tests pass with 19 expected PostgreSQL-only skips and 93% coverage. Frontend
build/typecheck/lint and all 251 tests pass. Independent Standards and Spec reviews were addressed.

## Next Run

Run `007L-sanction-workbench-contract-and-browser-closure`, then
`007M-exception-supporting-evidence-and-register-closure`. Both were inspected and already contain
concrete fields, role/action rules, exact browser specs, and screenshot contracts. Do not close
Epic 007 browser/fidelity evidence until `007N` also completes.
