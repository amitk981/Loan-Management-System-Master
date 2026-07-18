# Execution Plan

Selected slice: 009G5-legal-migration-state-guard-closure

## Scope and constraints

- Replace the shared, business-specific AST heuristic with a legal-owned guard whose interface
  reports actual `DocumentChecklist` project-state changes operation by operation.
- Preserve disbursements migration 0005 and legal migration 0015 byte-for-byte; add no migration,
  schema SQL, API, checklist-status, or production workflow behavior.
- Retain only the two exact historical operation identities from disbursements 0005. The exception
  will be immutable and will match the migration path, operation class, operation position, and
  expected before/after checklist-state fingerprints.
- All intended edits are permitted by `.ralph/permissions.json`: backend/test paths under
  `sfpcl_credit/**`, working/run evidence under `docs/working/**` and `.ralph/runs/**`, the selected
  and next slice files under `docs/slices/**`, plus Ralph state/progress bookkeeping.

## TDD sequence

1. RED: move the architecture-review module-constant bypass into the retained ownership test and
   prove the current AST guard misses it. Save the focused failure output.
2. GREEN: introduce the smallest legal-owned state-transition interface and make the tracer test
   pass by comparing the checklist model state before/after each operation.
3. RED/GREEN incrementally add imported-operation, inherited-operation, helper-indirection,
   renamed path/class, changed-target, ordinary database-only `RunPython`, legal-owned future
   operation, and exact historical exception cases.
4. Remove the shared business-policy module after every caller uses the legal-owned interface;
   verify no shared file contains legal/disbursement policy tokens.

## Verification and evidence

- Run the focused ownership tests after every red/green cycle with
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python` and retain red/green logs.
- Run the complete 009G4 anchor manifest class plus adjacent migration-isolation tests, Django
  check, `makemigrations --check --dry-run`, and Python compilation. Do not run the full backend
  suite or full coverage; the orchestrator owns those authoritative gates.
- Confirm migration 0015 remains zero-operation and the replacement introduces no migration/model
  drift or SQL. Run applicable frontend gates only if a frontend file unexpectedly changes (none
  is planned).
- Review the final diff for protected paths, scope, dependency direction, and configured diff
  limits; save changed-files, risk assessment, review packet, final summary, and terminal evidence.
- Update the Epic 009 digest, selected slice status/checklist, Ralph state/progress/handoff, and
  sharpen the next one or two Not Started slices only from already-opened source material.
