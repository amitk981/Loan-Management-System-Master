# Execution Plan

Selected slice: 008K3-final-checklist-evidence-closure

1. Inspect the existing checklist action owner, immutable cross-owner security evidence contract,
   models/migrations, and the 008K API/PostgreSQL tests. Map each current checklist item to the
   exact source-owned terminal facts required by the slice without widening sensitive-data access.
2. TDD RED: add focused public-API regressions proving that Company Secretary approval rejects
   status-only/bulk-completed items and blank-cheque completion rejects synthetic version JSON.
   Save the failing output in `evidence/terminal-logs/`.
3. Implement the narrow evidence seam and checklist reconciliation: resolve current cheque and
   legal/security aggregates by exact ids, freeze a deterministic terminal digest and authorised
   stage role in every action, and require one exact immutable completion action for every current
   required/applicable item before Company Secretary approval. Preserve A-101 and the blocked
   finance signature boundary.
4. Extend the public terminal matrix and adverse tests across PoA, tri-party, SH-4/CDSL,
   signatures/mismatch, cheque/custody, Term Sheet threshold, Loan Agreement, and final checklist.
   Cover multi-role canonical attribution, exact/changed replay, stale/cross-object evidence, and
   zero-write rejection. Add a migration only if persisted action fields are required.
5. Strengthen the declared PostgreSQL five-worker races for item completion and all approval
   stages so the sole material winner owns the retained payload/request/action/audit/version/
   workflow identities and every changed loser owns none; run each race suite twice.
6. Run focused green tests, Django check and migration sync, the full backend coverage gate, and
   all frontend lint/typecheck/test/build gates. Save self-contained terminal evidence and record
   any environment-only PostgreSQL limitation honestly.
7. Perform separate Standards and Spec review passes against `HEAD` and this slice, correct any
   findings, then finalize changed-files, risk assessment, review packet, final summary, state,
   progress, handoff, slice status, digest/context/API-contract notes if affected, and sharpen the
   next one or two Not Started slices using only already-opened source material.
