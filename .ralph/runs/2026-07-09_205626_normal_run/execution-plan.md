# Execution Plan

Selected slice: 005F-deficiency-creation-and-resolution

## Scope

Implement backend/API deficiency creation and read access for submitted loan applications, using the
005E completeness workbench as the source of valid deficiency facts.

## Source Trace

- `docs/source/implementation-roadmap.md` §11.2-§11.7: completeness APIs create deficiencies;
  incomplete applications can be returned with deficiencies; critical actions are audit logged.
- `docs/source/api-contracts.md` §19.7 and §21.1-§21.2: return-with-deficiencies, list
  deficiencies, and resolve deficiency endpoints.
- `docs/source/data-model.md` §13.5, §33.1, §34.1: `deficiencies` fields,
  `ApplicationReturnedWithDeficiencies` event payload, and atomic deficiency return.
- `docs/source/screen-spec.md` §9.1: incomplete applications must be returned with a deficiency
  list.
- `docs/source/screen-spec-member-portal.md` MP11/§8.2: borrower response/resubmission is a later
  portal flow; this slice exposes records for that later UI.

## Implementation Steps

1. Add failing API regression tests in `sfpcl_credit/tests/test_loan_applications_api.py` for:
   successful return with source-backed deficiency items and metadata-only audit/workflow evidence;
   empty/arbitrary item validation; invalid states; permission/object-scope denials; list/read
   behavior and sensitive-data exclusion.
2. Add `ApplicationDeficiency` model and one migration with source-backed fields:
   application, item code/type/category/reason, description/remarks, status, raised/resolved actor
   stamps, communication mode/message metadata.
3. Extend application services to:
   - derive allowed return items from `build_completeness_workbench`;
   - create open deficiency rows atomically from selected blocking document codes;
   - set the application completeness status to incomplete without generating references or
     register rows;
   - serialize/list/read deficiencies; and
   - resolve open deficiencies if the API contract has enough exact fields.
4. Add endpoints and URL routes:
   - `POST /api/v1/loan-applications/{id}/return-with-deficiencies/`
   - `GET /api/v1/loan-applications/{id}/deficiencies/`
   - `POST /api/v1/deficiencies/{id}/resolve/`
5. Update `docs/working/API_CONTRACTS.md` and the Epic 005 digest with implemented facts.
6. Run targeted red/green tests first, then required backend and frontend gates, saving logs under
   `.ralph/runs/2026-07-09_205626_normal_run/evidence/terminal-logs/`.
7. Save API examples, changed files, risk assessment, review packet, final summary, and update
   state/progress/handoff/slice status. Sharpen the next 1-2 not-started slices from already opened
   source/digest context.
