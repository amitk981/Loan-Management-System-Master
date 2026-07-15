# Execution Plan

Selected slice: `008K5-final-evidence-authority-and-migration-closure`

1. Trace the application-owned immutable bank-decision boundary, checklist reconciliation,
   legal/application migration graph, ordinary security projections, and the two existing
   generation races. Inventory the exact durable ledgers and current-evidence selectors each path
   is required to reconcile.
2. Add focused failing tests first for canonical Stage-4 bank scope and the §6.3 action response;
   changed/missing/extra/cross-object borrower-safe evidence; legal-owned migration anchoring;
   real-row ordinary-reader DTO allowlists; and exact winner/loser generation-race ledgers. Save
   the red output in `evidence/terminal-logs/`.
3. Implement the smallest module/API/migration changes that make those tests pass: enforce object
   and workflow scope within `applications`, make every reconciliation predicate unconditional,
   add a state-only `legal_documents` migration anchor after `applications.0016`, and preserve the
   existing redacted public DTO and coordinator boundaries.
4. Run focused green tests, migration forward/reverse/fresh-plan checks, both declared PostgreSQL
   five-worker races twice, then backend check/migration/coverage gates and all frontend gates.
   Retain self-contained terminal evidence and sanitized API/DTO/migration summaries.
5. Review the diff against the selected slice and protected-path/diff limits; update API contracts,
   slice status, Ralph state/progress/handoff, the Epic 008 digest, and sharpen the next one or two
   eligible Not Started slices using only requirements already opened. Complete changed-files,
   risk assessment, review packet, and final summary without committing or pushing.
