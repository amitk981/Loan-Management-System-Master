# Slice 005F2: Deficiency Return Status Contract Hardening

## Status
Not Started

## Parent Epic
Epic 005: Loan Application Intake, Documents, Completeness, and Deficiencies
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal
Close the architecture-review finding from `2026-07-09_213305_architecture_review` before member
portal authentication and status screens build on deficiency return state.

## User Value
Staff and borrowers see a returned incomplete application as a distinct workflow state, not as a
plain submitted application with hidden deficiency metadata.

## Depends On
- 005F

## Prior Slice Facts
- 005F implemented deficiency rows and endpoints:
  `POST /api/v1/loan-applications/{loan_application_id}/return-with-deficiencies/`,
  `GET /api/v1/loan-applications/{loan_application_id}/deficiencies/`, and
  `POST /api/v1/deficiencies/{deficiency_id}/resolve/`.
- 005F currently keeps `application_status = submitted` and sets only `completeness_status =
  incomplete` when returning deficiencies.
- 005F already blocks reference-generated applications, creates no loan request register row,
  generates no `LO...` reference, and advances no visible sequence when returning deficiencies.
- 005F already records A-040 for accepting `items[].item_code` instead of source §19.7
  `deficiency_ids`; preserve that request-shape decision unless the source is updated.

## Source References
- `docs/source/data-model.md` `loan_application_status` enum includes `incomplete_returned`.
- `docs/source/functional-spec.md` M03 deficiency flow says an incomplete application enters the
  incomplete state and keeps deficiency history.
- `docs/source/screen-spec.md` S12 deficiency flow says returned applications become
  `Incomplete - Returned to Applicant` or rejected, depending on business decision.
- `docs/working/digests/epic-005-application-intake.md` status-contract extract from the
  `2026-07-09_213305_architecture_review`.

## Prototype Reference
None.

## Screens Involved
None directly. This slice is backend/API contract hardening before portal status UI.

## Frontend Scope
None.

## Backend/API Scope
Add the source-backed returned-incomplete application status:
- `LoanApplication.STATUS_INCOMPLETE_RETURNED = "incomplete_returned"`.
- Include the status in model validation and any local status vocabulary used by serializers/tests.
- `return_application_with_deficiencies(...)` must set:
  - `application_status = incomplete_returned`;
  - `completeness_status = incomplete`;
  - `current_stage = initial_loan_request` unless a source-backed queue/stage owner already exists.
- `return_deficiencies_invalid_state_message(...)` must still allow the first return only from a
  submitted, non-reference-generated application with no loan request register entry.
- Decide explicitly whether additional deficiency returns are allowed from `incomplete_returned`.
  If source docs do not define repeat-return behavior, keep repeat returns blocked and record the
  assumption rather than creating duplicate open deficiencies.
- Update `docs/working/API_CONTRACTS.md` and `docs/working/digests/epic-005-application-intake.md`
  with the corrected status behavior.

## Database/Model Impact
No migration expected unless status values are persisted in a database enum or reference table.

## API Contracts
Return-with-deficiencies responses and serialized application detail should show
`application_status = "incomplete_returned"` after a successful return.

## Permissions
Preserve 005F permissions and object-access ordering:
- Return and resolve require `applications.loan_application.complete_check`.
- List requires `applications.loan_application.read`.
- Unknown records return `404 NOT_FOUND`.
- Missing global permission returns `403 PERMISSION_DENIED`.
- Same-permission actors outside application scope return `403 OBJECT_ACCESS_DENIED`.

## Audit Requirements
Metadata-only audit and workflow evidence must record the old submitted status and new
`incomplete_returned` status. Continue to exclude raw file bytes, storage keys, checksums, PAN,
Aadhaar, full bank values, encrypted tokens, and hashes.

## Validation Rules
- Submitted applications with current blocking checklist facts can be returned with deficiencies.
- Draft applications, reference-generated applications, applications with register rows, and repeat
  returns from `incomplete_returned` are rejected with standard invalid-state behavior unless a
  source-backed repeat-return rule is found.
- Returning deficiencies still creates no reference, no loan request register entry, no credit
  assessment transition, and no visible sequence advancement.

## Test Cases
TDD backend tests first:
- Failing regression: successful return-with-deficiencies should return and persist
  `application_status = incomplete_returned` plus `completeness_status = incomplete`.
- Audit old/new values and workflow event should show `submitted -> incomplete_returned`.
- Repeat return from `incomplete_returned` is blocked without duplicate deficiency rows unless a
  source-backed repeat-return rule is recorded.
- Existing permission/object-scope denials still create no deficiency, audit, workflow, register,
  reference, or sequence side effects.

## Visual Acceptance Criteria
None.

## Evidence Required
Backend red/green logs, focused deficiency tests, and standard quality-gate logs.

## Risk Level
Medium

## Acceptance Criteria
- Deficiency return status matches the source-backed `incomplete_returned` lifecycle.
- Tests cover persisted status, API response status, audit/workflow transition evidence, and
  no-downstream-side-effect guarantees.
- No production scope beyond deficiency return status hardening is introduced.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Database rules followed, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
