# Execution Plan: 005A Loan Application Draft Create Update

## Scope
- Implement draft loan-application persistence and API endpoints only:
  - `POST /api/v1/loan-applications/`
  - `GET /api/v1/loan-applications/{id}/`
  - `PATCH /api/v1/loan-applications/{id}/`
- Keep submit, completeness, reference-number generation, document verification,
  deficiency workflow, eligibility, loan limits, appraisal, sanction, and
  disbursement out of scope.

## Source Trace
- `docs/source/api-contracts.md` §19.2-19.4 defines create, retrieve, and patch
  loan-application API surfaces.
- `docs/source/data-model.md` §13.1 requires loan applications to reference a
  member, requested amount, purpose, status/stage, and actor audit fields.
- `docs/source/auth-permissions.md` §12.4 and §39 require create/read/update
  permissions for the loan-application endpoints.
- `docs/source/screen-spec.md` S10 and member portal MP05/MP06 require draft
  save/resume with member, requested amount, purpose, land/crop, bank, and
  declaration facts.

## Permission Check
- Editable code paths are under `sfpcl_credit/**`, allowed by `.ralph/permissions.json`.
- Editable working docs are under `docs/working/**`, allowed.
- Slice sharpening is under `docs/slices/**`, allowed.
- Run artifacts are under `.ralph/runs/**`, allowed.
- No protected or forbidden paths will be modified.

## TDD Plan
1. Red: API create/read draft test proves a permitted user can create a draft,
   read it back with metadata-only member/bank summaries, and audit metadata
   omits sensitive identifiers.
2. Green: add `applications` app model/service/views/URL/migration enough to pass.
3. Red: patch validation/ownership test proves only draft fields update and
   cross-member subresource references are rejected.
4. Green: implement update and reference ownership validation.
5. Red: permission/negative validation test proves missing permissions,
   unknown member, malformed UUIDs, and non-positive amounts fail with standard
   envelopes.
6. Green/refactor: tighten service boundary and run full gates.

## Evidence
- Save red/green backend test output under
  `.ralph/runs/2026-07-09_172309_normal_run/evidence/terminal-logs/`.
- Save API response examples in the run folder.
- Save final changed files, risk assessment, review packet, final summary, and
  update Ralph state/progress/handoff/slice status.
