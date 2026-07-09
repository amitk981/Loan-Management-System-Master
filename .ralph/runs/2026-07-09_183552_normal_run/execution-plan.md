# Execution Plan

Selected slice: 005C-reference-number-generation-and-loan-request-register

## Source Decision

The selected source sections say the official `LO00000001` sequence is assigned after the
application completeness check passes:

- `docs/source/screen-spec.md` §4.4: Application Reference Number starts at `LO00000001` and is
  assigned after completeness check.
- `docs/source/screen-spec.md` S12: completeness check verifies the submitted application before
  generating the official reference; when mandatory checks pass, the system generates the
  sequential reference, creates a Loan Request Register entry, changes status to Reference
  Generated, and moves the application to appraisal.
- `docs/source/screen-spec-member-portal.md` MP submission copy: borrower receives the reference
  number after submitted details and documents are checked.
- `docs/source/data-model.md` §13.2: `system_sequences` generates business sequences atomically.

005C will therefore add a narrow backend action that represents the successful completeness-pass
reference generation point. It will not implement checklist verification, deficiencies, documents,
eligibility, appraisal, sanction, disbursement, frontend wiring, or broad register management UI.

## Implementation Steps

1. Add a red API regression test for `POST /api/v1/loan-applications/{id}/generate-reference/`:
   submitted applications with the completeness-check permission receive `LO00000001`, persist it
   on the application, create one register entry, write metadata-only audit/workflow evidence, and
   expose the register summary in the response without sensitive values.
2. Add a second red/green cycle for sequential uniqueness and duplicate/draft validation.
3. Implement the smallest backend model changes:
   - `SystemSequence` for `loan_application_reference` with `LO` prefix and 8-digit padding.
   - `LoanRequestRegisterEntry` linked one-to-one to `LoanApplication`.
   - one migration for both tables.
4. Add service/view/url support for the narrow reference-generation action using the existing
   `applications.loan_application.complete_check` permission and standard API envelopes.
5. Update `docs/working/API_CONTRACTS.md`, `docs/working/ASSUMPTIONS.md` if needed, and the Epic
   005 digest with the exact trigger decision.
6. Run targeted red/green tests and then the required Ralph gates:
   backend check, backend tests, backend migration check, backend coverage, frontend build,
   frontend typecheck, frontend lint, and frontend test.
7. Save API examples, terminal logs, changed files, risk assessment, review packet, final summary,
   and update state/progress/handoff/slice status. Sharpen the next 1-2 Not Started slices using
   only the source material already opened.
