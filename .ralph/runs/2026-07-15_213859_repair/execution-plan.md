# Execution Plan

Selected slice: CR-008-document-template-constraint-migration-nondeterminism

## Diagnosed Failure

The newest stored Ralph failure summary belongs to the already-repaired 008L4 browser run, so it
does not describe this selected CR. CR-008 instead repairs the accepted GitHub Actions failure:
`DocumentTemplate` and its historical `0002` migration use unordered sets inside migration-facing
`Q(...__in=...)` expressions, allowing Django migration-state deconstruction to vary by Python hash
seed.

## Plan

1. Capture the current multi-seed migration-check symptom and add one focused documents-module
   regression test that requires ordered, exact values for both migration-facing constraints.
2. Save the failing test output under `evidence/terminal-logs/` before changing the model.
3. Replace only the current model constraint RHS collections with deterministic tuples and add one
   forward documents migration that removes/re-adds the same named database constraints with the
   same exact values; do not rewrite historical migration `0002`.
4. Run the focused regression and document-template API tests, saving green evidence.
5. Run `makemigrations --check --dry-run` under representative `PYTHONHASHSEED` values and verify
   every run reports `No changes detected`.
6. Run backend check, migration sync, full backend coverage, and all configured frontend gates even
   though no frontend behavior changes.
7. Save changed-files, risk, review, and final evidence; update the selected slice, state, progress,
   handoff, and sharpen the next one to two Not Started slices only from already-opened sources.

## Guardrails

- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command.
- No source-document, protected-file, frontend, endpoint, service, permission, or business-rule
  changes.
- Preserve constraint names, allowed values, null handling, and database enforcement exactly.
