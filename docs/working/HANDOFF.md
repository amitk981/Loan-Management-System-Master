# Ralph Handoff

## Last Run
2026-07-09_175511_normal_run

## Current Status
`005B-application-submit-and-status-transition` completed successfully.

## What Completed
- Added `POST /api/v1/loan-applications/{loan_application_id}/submit/`.
- Submit requires `applications.loan_application.submit`.
- Submit permits only `draft -> submitted` and returns `409 INVALID_STATE_TRANSITION` for repeat or
  non-draft submits.
- Submit stamps `submitted_at` and `submitted_by_user`, updates `updated_at`/`updated_by_user`, and
  preserves `current_stage = initial_loan_request`, `completeness_status = not_started`, and
  nullable `application_reference_number`.
- Submitted applications remain readable through `GET /api/v1/loan-applications/{id}/`.
- Draft `PATCH` now rejects submitted applications through the existing draft-only validation path.
- Submit validates the persisted 005B request facts: borrower member, positive
  `required_loan_amount`, nonblank `declared_purpose`, and nonblank `purpose_category`.
- Successful submit writes metadata-only `applications.loan_application.submitted` audit and a
  `loan_application` workflow event from `draft` to `submitted`.
- Submit responses and audit metadata preserve 005A/Epic 004 sensitive-data boundaries:
  no PAN, Aadhaar, full bank account numbers, token values, or hashes; selected bank metadata still
  uses `account_holder_name`, masked account values, and `can_view_full: false`.
- Updated `docs/working/API_CONTRACTS.md`, `docs/working/ASSUMPTIONS.md`, and
  `docs/working/digests/epic-005-application-intake.md`.
- Sharpened `005C-reference-number-generation-and-loan-request-register` and
  `005D-application-document-checklist`.

## Explicit Deferrals
- Formal `LO...` reference generation and loan request register remain `005C`.
- `submission_notes` is accepted as JSON but not persisted; no source-backed column exists yet.
- Nominee checks, application document placeholders, document checklist, completeness check,
  deficiencies, eligibility, loan limit, appraisal, sanction, disbursement, payment initiation,
  member portal flows, and frontend application wiring remain future slices.
- A-036 records that the broader source submit gate mentions nominee/document placeholders, but
  005B deliberately leaves those to document/completeness slices.

## Evidence
See `.ralph/runs/2026-07-09_175511_normal_run/`.

Key artifacts: `execution-plan.md`, `review-packet.md`, `risk-assessment.md`,
`changed-files.txt`, `final-summary.md`, `api-response-examples.md`, and gate logs under
`evidence/terminal-logs/`.

No visual evidence was required because 005B was backend/API-only.

## Notes For Next Run
- Run `005C-reference-number-generation-and-loan-request-register` next.
- 005C must re-check the exact source-backed trigger for formal `LO...` generation because the
  portal copy says borrowers receive the reference number after submitted details/documents are
  checked.
- Keep document checklist verification, completeness, deficiencies, eligibility, appraisal,
  sanction, disbursement, and frontend wiring out of 005C unless the selected slice is explicitly
  rewritten.
- Use `docs/working/digests/epic-005-application-intake.md` before reopening large source docs.
