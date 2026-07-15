# Review Packet: 2026-07-15_213859_repair

## Result
Complete; ready for independent orchestrator validation and commit.

## Slice
CR-008-document-template-constraint-migration-nondeterminism

## Diagnosis and Change

Python sets in both current `DocumentTemplate.Meta.constraints` and historical migration state
deconstructed with hash-dependent iteration order. The focused regression reproduced that exact
symptom for both named constraints. Current model state now uses ordered tuples, while new forward
migration `documents.0005` removes and recreates the same constraints with the same exact values.
Historical migration `0002` was not edited.

## Files for Review

- `sfpcl_credit/documents/models.py`
- `sfpcl_credit/documents/migrations/0005_deterministic_document_template_constraints.py`
- `sfpcl_credit/tests/test_document_template_migration_state.py`
- Ralph status/handoff/digest/slice-sharpening and this run's evidence artifacts.

## Traceability

The repository CI contract in `.github/workflows/ci.yml` requires
`makemigrations --check --dry-run`. The accepted CR requires both template constraint collections to
serialize deterministically without changing allowed values, names, or enforcement. The model and
forward migration retain `doc_template_approval_status` with `draft`, `approved`, `retired`, and
`doc_template_borrower_type` with nullable `individual_farmer`, `fpc`, `fpo`. This is verified by
`DocumentTemplateMigrationStateTests`, the exact five-seed migration-check matrix, database insert
enforcement, and the existing document-template API tests.

## Validation

- RED: focused test reported four failures because model and terminal migration values were sets.
- GREEN: 2 focused migration/constraint tests and 10 existing template tests passed (2 expected
  PostgreSQL-only concurrency skips in the targeted group).
- Hash seeds `0`, `1`, `42`, `123456`, and `random`: `No changes detected` every time.
- Backend: Django check/migration sync green; 900 tests passed, 46 expected skips; 91% coverage.
- Frontend unchanged: lint, typecheck, 305 tests, and build green.
- Protected paths and historical migration `documents.0002` unchanged; `git diff --check` green.

## Recommended Next Action

Allow the orchestrator to validate and commit CR-008, then run
`008M-documentation-hub-frontend-wiring`.
