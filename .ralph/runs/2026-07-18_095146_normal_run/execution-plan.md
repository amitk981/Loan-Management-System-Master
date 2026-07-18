# Execution Plan

Selected slice: 009G4-legal-checklist-migration-ownership-anchor

1. Extend the focused legal-checklist migration test boundary to cover the state immediately before
   disbursements 0005, the current legal/disbursement/communications leaves, and a new legal-owned
   anchor. Preserve a real checklist and action row while comparing exact constraint names, physical
   schema, ids, and values through forward, reverse, and reapply.
2. Add a static migration-ownership guard test that scans custom migration operations for mutations
   of `legal_documents.DocumentChecklist`. Prove a synthetic downstream mutation is rejected and
   the single reviewed historical exception, disbursements 0005, is accepted.
3. Run the focused test first and retain the failing output. Add exactly one empty/state-only
   `legal_documents` migration whose dependencies anchor legal 0014, disbursements 0005 and 0007,
   and communications 0004 without replaying SQL. Make the focused tests green and save red/green
   logs plus a SQL/state manifest.
4. Run Django check, migration sync, the impacted legal migration-isolation tests, Python compile,
   and the applicable frontend build/typecheck/lint/test gates. Do not run the complete backend
   suite or coverage; the orchestrator owns those authoritative gates.
5. Record changed files, high-risk zero-data-loss assessment, source-to-test traceability, final
   summary, and durable Epic-009 digest. Mark only 009G4 complete, update Ralph state/progress and
   handoff, and recheck the next two Not Started slices for concrete requirements before finishing.

## Repair Plan — 2026-07-18_101754_repair

1. Reproduce the independent coverage failure with the exact historical credit-ownership migration
   test and preserve the red output.
2. Inspect only the migration projection boundary implicated by the traceback. Confirm whether the
   new legal-owned leaf makes the historical pre-move registry outrun `applications.0010`.
3. If confirmed, extend that retained test's downstream-app exclusion boundary by the smallest
   necessary app label; do not alter production migrations, models, or 009G4 behavior.
4. Re-run the exact failing class twice, then the focused 009G4 and adjacent migration-isolation
   tests, Django check, migration sync, and compilation. Leave the complete backend suite and
   coverage to independent orchestrator revalidation.
5. Update repair evidence and run artifacts while preserving the completed slice implementation.
