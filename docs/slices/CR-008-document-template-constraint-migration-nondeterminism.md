# Slice CR-008: Make document-template constraint migrations deterministic

## Status
Complete

## Origin
Change request (maintenance stage), accepted 2026-07-15 from docs/change-requests/accepted/CR-008-document-template-constraint-migration-nondeterminism.md.

## Risk Level
High

## Change Request (verbatim)

# Make document-template constraint migrations deterministic

## Type
bug-backend

## Severity
High

## What Is Happening
GitHub Actions intermittently fails the backend `makemigrations --check --dry-run`
gate by proposing a new `documents` migration that removes and recreates
`doc_template_approval_status` (and may also be sensitive to the borrower-type
constraint). The affected model and historical migration pass unordered Python
`set` values into migration-facing `Q(...__in=...)` expressions. Their serialized
ordering is process/platform-dependent, so a clean application commit can be
reported as having missing migrations and the Ralph loop cannot advance.

## Expected Behaviour
Document-template constraints must have a deterministic deconstruction on every
machine and Python hash seed. A clean checkout must always report `No changes
detected` from Django's migration check.

## Steps To Reproduce
1. Push a clean `staging` commit that includes the current `DocumentTemplate`
   constraints to GitHub Actions.
2. Let the backend CI job run
   `python sfpcl_credit/manage.py makemigrations --check --dry-run`.
3. On an affected runner, observe Django propose a `documents/0005_...` migration
   that removes and recreates `doc_template_approval_status`, then exit with code
   1 even though no intentional schema change was made.
4. Compare `sfpcl_credit/documents/models.py` and migration `0002`: both use
   unordered sets for `approval_status__in` and `borrower_type__in`.

## Where It Appears
GitHub Actions backend CI migration gate; `DocumentTemplate.Meta.constraints` in
`sfpcl_credit/documents/models.py` and the `documents` migration state.

## Source Document Reference
Repository migration contract: `.github/workflows/ci.yml` requires
`makemigrations --check --dry-run`; the approved document-template status and
borrower-type values remain unchanged. This repair changes only deterministic
serialization, not business behaviour.

## Acceptance Criteria
- Both document-template `__in` constraint value collections use a deterministic
  ordered representation in current model state.
- Historical applied migrations are not rewritten; a forward migration aligns
  the recorded constraint state with the deterministic model definition if
  Django requires one.
- The allowed approval statuses and borrower types, constraint names, and
  database enforcement remain exactly unchanged.
- A regression test fails if unordered collections are reintroduced into
  migration-facing document-template constraints.
- `makemigrations --check --dry-run` reports `No changes detected` across a
  representative matrix of `PYTHONHASHSEED` values.
- Targeted document-template tests, the full backend suite, and coverage pass.
- No frontend files or frontend behaviour change.

## Mandatory First Step: Impact Analysis
Before changing ANY code, write impact-analysis.md in the run folder covering:
- Affected backend models/endpoints/services, with grep evidence.
- Affected frontend screens/components/routes.
- Blast radius: every OTHER module that consumes the affected pieces.
- Existing tests covering the affected pieces, and the regression tests to add in EACH affected module.
- FRONTEND_DESIGN_RULES compliance note for any UI change.
Validation fails this run if impact-analysis.md is missing.

## Acceptance Criteria
- The change request's own acceptance criteria are met.
- Regression tests added for every module named in the impact analysis.
- All quality gates pass.
