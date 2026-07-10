# Execution Plan: 005H Rejection Note Shell

## Scope
- Implement the staff-only rejection-note metadata shell for loan applications.
- Add at most one application migration for `rejection_notes`.
- Expose source-backed endpoints:
  - `POST /api/v1/loan-applications/{loan_application_id}/rejection-note/`
  - `POST /api/v1/rejection-notes/{rejection_note_id}/send/`
- Do not add frontend wiring unless required by the backend contract; current slice permits backend/API-only.

## Source Facts
- `docs/source/api-contracts.md` §21.3-§21.4 defines create/send rejection-note endpoints and request fields.
- `docs/source/data-model.md` §13.6 defines `rejection_notes` metadata fields.
- `docs/source/screen-spec.md` S14 requires mandatory detailed reason, reason category, stage, reapply flag, communication mode, and future formal note actions.
- Existing Epic 005 facts require no `LO...` reference, register row, sequence advancement, appraisal, sanction, or borrower portal action side effects.

## Permissions And State
- Use staff authentication and existing application object-access ordering.
- Require `applications.loan_application.complete_check` because source places rejection alongside completeness/deficiency handling and no narrower rejection permission exists yet.
- Allow create only for submitted, non-reference-generated applications without register rows.
- Keep `incomplete_returned` separate and invalid for rejection-note creation.
- Send is a metadata status transition only; no real communication delivery.

## TDD Steps
1. Add failing API tests for successful create/send, permission/object scope, portal token rejection, suspended portal session invalidation, invalid state, duplicate/send rules, and metadata-only side effects.
2. Add `RejectionNote` model and migration.
3. Add services, serializers, views, and URL routes reusing existing envelope/audit/workflow patterns.
4. Update API contracts, digest/assumptions if needed, slice status, handoff, progress/state, and run evidence.
5. Run focused red/green tests, then full backend/frontend gates required by Ralph.

## Files Expected To Change
- `sfpcl_credit/applications/models.py`
- `sfpcl_credit/applications/services.py`
- `sfpcl_credit/applications/views.py`
- `sfpcl_credit/applications/migrations/0006_rejection_note.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/tests/test_loan_applications_api.py`
- `docs/working/API_CONTRACTS.md`
- Ralph state/progress/handoff/slice/evidence artifacts.
