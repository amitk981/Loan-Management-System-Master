# Review Packet

## Slice
005F2-deficiency-return-status-contract-hardening

## Summary
Deficiency return now uses the source-backed returned-incomplete status. A successful
`return-with-deficiencies` action changes a submitted application to:

- `application_status = incomplete_returned`
- `completeness_status = incomplete`
- `current_stage = initial_loan_request`

The API response, persisted application detail, audit metadata, and workflow event all expose that
contract. Repeat returns from `incomplete_returned` are blocked pending a future source-backed
resubmission flow.

## Traceability
- Source says `loan_application_status` includes `incomplete_returned`
  (`docs/source/data-model.md`).
  Code adds `LoanApplication.STATUS_INCOMPLETE_RETURNED` and allows it in model validation.
  Verified by `test_return_with_deficiencies_creates_open_records_from_blocking_checklist_items`.
- Source says incomplete applications enter the incomplete/deficiency-raised state and keep
  deficiency history (`docs/source/functional-spec.md` M03 deficiency flow).
  Code sets returned applications to `incomplete_returned`, keeps deficiency rows, and keeps the
  completeness status `incomplete`.
  Verified by response, persisted model, deficiency-list, audit, and workflow assertions.
- Source says S12 returned applications become `Incomplete - Returned to Applicant` or rejected.
  Code implements the returned-incomplete path and preserves no-reference/no-register/no-sequence
  side effects.
  Verified by focused tests asserting no register row, no sequence row, no reference number, and no
  duplicate side effects on repeat returns.

## Files Of Interest
- `sfpcl_credit/applications/models.py`: added status constant and validation.
- `sfpcl_credit/applications/services.py`: return-with-deficiencies state transition now writes
  `incomplete_returned` and workflow evidence.
- `sfpcl_credit/tests/test_loan_applications_api.py`: regression coverage for response,
  persistence, detail serialization, audit/workflow transition, repeat-return rejection, and
  no-downstream-side-effect guarantees.
- `docs/working/API_CONTRACTS.md`: updated return-with-deficiencies contract.
- `docs/working/ASSUMPTIONS.md`: added A-041 for blocked repeat returns.
- `docs/working/digests/epic-005-application-intake.md`: updated Epic 005 digest.

## Evidence
- Red: `evidence/terminal-logs/red-focused-deficiency-return-status.log`
- Green: `evidence/terminal-logs/green-focused-deficiency-return-status.log`
- Focused module: `evidence/terminal-logs/focused-loan-applications-api.log`
- Backend gates: `backend-check.log`, `backend-tests.log`, `backend-makemigrations-check.log`,
  `backend-coverage.log`
- Frontend gates: `frontend-lint.log`, `frontend-typecheck.log`, `frontend-test.log`,
  `frontend-build.log`
- Diff hygiene: `git-diff-check.log`

## Gate Results
- Backend check: passed.
- Backend focused loan application API tests: 18 passed.
- Backend full tests: 256 passed.
- Backend migrations check: no changes detected.
- Backend coverage: 95%, floor 85%.
- Frontend lint: passed.
- Frontend typecheck: passed.
- Frontend tests: 80 passed.
- Frontend build: passed.
- `git diff --check`: passed.
