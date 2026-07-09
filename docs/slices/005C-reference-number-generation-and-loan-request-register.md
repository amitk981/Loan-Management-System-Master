# Slice 005C: Reference Number Generation and Loan Request Register

## Status
Not Started

## Parent Epic
Epic 005: Loan Application Intake, Documents, Completeness, and Deficiencies
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal
Deliver this narrow capability as a small, testable Ralph implementation slice.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 005B

## Prior Slice Facts
- 005A created persisted loan-application drafts with nullable `application_reference_number`.
- 005B implemented `POST /api/v1/loan-applications/{loan_application_id}/submit/` with source-backed
  permission `applications.loan_application.submit`.
- 005B permits only `draft -> submitted`, stamps `submitted_at` and `submitted_by_user`, preserves
  `current_stage = initial_loan_request`, keeps `completeness_status = not_started`, locks direct
  `PATCH` updates after submit, and leaves `application_reference_number` nullable.
- 005B recorded A-035/A-036: the member portal source says the formal `LO...` reference is received
  after submitted details/documents are checked; nominee/document placeholder gates remain future
  document/completeness work. Re-check the exact reference trigger before implementing 005C.
- Use `docs/working/digests/epic-005-application-intake.md` before reopening large source docs.
- Epic 004/005A sensitive data boundaries remain binding: register rows, audit metadata, and
  responses must not include full PAN, Aadhaar, full bank account numbers, token values, or hashes.

## Source References
- docs/source/implementation-roadmap.md section 11
- docs/source/api-contracts.md sections 19-21
- docs/source/data-model.md loan origination tables
- docs/source/screen-spec.md application screens
- docs/source/screen-spec-member-portal.md application screens

## Prototype Reference
- sfpcl-lms/src/pages/applications/*
- sfpcl-lms/src/pages/borrower/portal/applications/*

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
Implement the named backend/API capability only.

Concrete 005C scope:
- Add source-backed formal loan-application reference generation using a sequence that starts at
  `LO00000001` and produces unique values for applications that have reached the source-backed
  reference-generation point.
- Create and persist loan request register entries only for the submitted/pre-completeness
  applications that receive a formal reference in this slice. Keep register data sourced from the
  existing loan application/member record; do not copy sensitive identifiers into the register.
- Decide from the opened source sections whether the reference is generated at submit, immediately
  after submit, or during completeness check. If unresolved, follow A-035 and record the transition
  chosen in `docs/working/ASSUMPTIONS.md`.
- Expose only the narrow API needed for the reference/register capability. If no public action is
  source-backed, implement it behind the existing submit/completeness path and document the
  contract; do not invent a broad register management UI in this slice.
- Do not implement document checklist verification, deficiency workflow, eligibility, loan limit,
  appraisal, sanction, disbursement, or frontend wiring in 005C.

## Database/Model Impact
Non-destructive model/migration changes for this capability, if needed.

Expected model impact:
- A sequence/config table or service-backed sequence row if the existing schema does not already
  support `LO...` generation.
- A `loan_request_register_entries` table only if needed for this slice, linked one-to-one to
  `loan_applications` and storing register metadata without sensitive identity/bank values.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Apply the role and object-access rules from `docs/source/auth-permissions.md`; classify unknown access as approval-required.

Use the existing loan-application permission that owns the transition triggering reference
generation. Do not invent register-admin permission codes unless the source sections opened during
005C name them.

## Audit Requirements
Record audit/workflow events for critical create/update/approval/access actions.

## Validation Rules
Enforce source-doc business rules and block invalid state transitions.

Specific validation to cover:
- Reject reference generation for unknown applications.
- Reject reference generation for draft applications if the chosen transition requires at least
  `submitted` status.
- Reject duplicate register/reference generation for an application that already has a formal
  reference or register entry.
- Ensure generated references are unique and zero-padded in the `LO00000001` style.
- Preserve nullable/no-reference behavior for drafts before the chosen transition.
- Do not let a failed/duplicate reference attempt create partial register rows, workflow events, or
  audit entries.

## Test Cases
Unit/service/API/permission tests plus frontend tests where UI is touched.

Minimum regression tests:
- First reference generated for a submitted application is `LO00000001` (or the configured starting
  value if a source/config row exists) and is persisted on the application.
- Two applications receive distinct sequential references without collisions.
- A loan request register entry is created once and links to the application/member/reference.
- Re-running the generation path is idempotent or returns a standard duplicate-state error, based
  on the source-backed transition chosen for 005C.
- Responses, audit rows, workflow events, and register rows contain no full PAN, Aadhaar, full bank
  account values, protected token values, or hashes.

## Visual Acceptance Criteria
None.

## Evidence Required
Test output, API response examples, and screenshots when frontend is touched.

## Risk Level
Medium

## Acceptance Criteria
- The named capability works through the intended backend/API/frontend path, where applicable.
- Source-doc business rules are enforced or documented as assumptions.
- Permissions and audit expectations are tested when applicable.
- The implementation stays within one small Ralph slice.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested, if needed
- [ ] Audit events tested, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
