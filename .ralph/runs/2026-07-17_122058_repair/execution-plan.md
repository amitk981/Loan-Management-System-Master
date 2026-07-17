# Execution Plan

Selected slice: 009E3-disbursement-amount-and-source-bank-governance-closure

## Demonstrated failure

- Preserve the existing uncommitted 009E3 implementation and repair only the three failures reported
  by the independent backend coverage gate in
  `LoanReadyDocumentChecklistFixture`: incoherent approved cases incorrectly create a checklist and
  missing/conflicting share-mode facts incorrectly make an item applicable.
- Build one focused, deterministic test command for the failing class before inspecting or changing
  implementation code; save its red and green results under `evidence/terminal-logs/`.

## Diagnosis and repair

1. Reproduce the exact failing class twice with the orchestrator-managed Python interpreter.
2. Minimise to the failing test methods and compare their full-suite import/class context with the
   original checklist test module.
3. Rank falsifiable hypotheses, then inspect only the imports, fixture inheritance, and 009E3 test
   changes implicated by the repro.
4. Add or retain a regression assertion at the real collection/import seam if one is required, and
   make the narrowest repair that removes the cross-module test contamination without weakening the
   production checklist contract or changing 009E3 behavior.

## Verification and handoff

- Re-run the exact red loop twice, the originating checklist module, and the focused 009E3 backend
  suites with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Run Django check, migration-sync check, and changed-scope lint/static dependency checks. Do not run
  the complete backend suite or coverage; independent revalidation owns those gates.
- Confirm no debug instrumentation or unrelated edits remain, then update the repair run's evidence,
  changed-files list, risk assessment, review packet, and final summary. Keep the already completed
  slice/state/handoff truth unless the repair materially changes it.
