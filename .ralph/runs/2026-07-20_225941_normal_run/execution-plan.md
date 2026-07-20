# Execution Plan

Selected slice: 010H3-interest-policy-and-reclassification-integrity-closure

1. Add public owner-level RED tests for approved calculation-policy immutability, explicit rounding
   at the approved whole-decision boundary, and capitalisation reconciliation with zero side effects
   on mismatch. Retain exact failing command output in `evidence/terminal-logs/`.
2. Add an approved interest-calculation policy owner and migration-backed rounding fields. Freeze an
   approved version immediately across model, queryset, bulk, deletion, and database paths; require
   amendments to be new separately approved rows.
3. Make invoice, accrual, and capitalisation consume the same approved rounding decision. Apply
   precision/mode once to the summed unrounded decision and fail closed when an approved policy does
   not define the supported rounding contract.
4. Reconcile invoice interest, account interest, schedule interest, payment applications through
   30 April, and the principal increment before any capitalisation side effect. Persist one atomic
   reclassification decision and preserve exact/changed-key replay and race behavior.
5. Add the declared five-test PostgreSQL acceptance class plus reverse-consumer coverage, then run
   focused GREEN tests, Django check, migration sync, and the trusted PostgreSQL class twice when the
   local database supports it. Do not run the complete backend suite locally.
6. Complete `review-closure-evidence.md`, risk assessment, review packet, final summary, and run the
   exact review-closure validator until it prints PASS. Delegate commit and all mechanical state,
   status, changed-file, progress, and handoff bookkeeping to the orchestrator.

Scope guard: backend interest/configuration ownership and retained run evidence only; no frontend,
new tax/fee/rate policy, unrelated servicing refactor, provider behavior, or source-document edits.
