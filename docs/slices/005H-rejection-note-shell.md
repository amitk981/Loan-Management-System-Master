# Slice 005H: Rejection Note Shell

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
- 005G

## Prior Slice Facts To Preserve
- Official `LO...` reference generation remains owned by completeness pass; rejection-note work
  must not generate references, register rows, sequences, or appraisal state.
- Returned deficient applications use `application_status = incomplete_returned`,
  `completeness_status = incomplete`, and `current_stage = initial_loan_request`; do not collapse
  those into plain `submitted`.
- Borrower portal users have only own-data portal permissions. Do not expose staff rejection-note
  creation, completeness, reference-generation, return-with-deficiencies, or deficiency-resolution
  actions through portal routes.
- 005FB/005G portal endpoints derive member scope from the active `PortalAccount`; staff rejection
  note endpoints must continue to use staff authentication, global permission checks, and object
  access boundaries.

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
Relevant prototype screen area for this capability.

## Frontend Scope
Small UI wiring for the named workflow, if applicable.

## Backend/API Scope
- Add the smallest staff-side rejection-note shell needed by the source application workflow.
- Reuse existing `LoanApplication` state/object-access helpers where possible.
- If the source-backed rejection-note persistence model is absent, add only the narrow model needed
  for metadata fields and auditability; do not add appraisal, sanction, document-generation, or
  borrower-letter delivery behavior in this slice.

## Database/Model Impact
Non-destructive model/migration changes for this capability, if needed.

## API Contracts
Create or update the API contract for this capability.

## Permissions
- Staff-only. Require the source-backed application read/object-access boundary plus the narrowest
  source-confirmed rejection/write permission available after reading the source sections.
- Borrower portal tokens must receive `403 PERMISSION_DENIED` for staff rejection-note actions.

## Audit Requirements
Record audit/workflow events for critical create/update/approval/access actions.

## Validation Rules
- Reject unknown applications with `404 NOT_FOUND`.
- Reject same-permission staff outside the application object scope with `403 OBJECT_ACCESS_DENIED`
  and no audit/workflow side effects.
- Reject invalid state transitions without creating rejection metadata, audit rows, workflow
  events, register rows, references, or sequence advancement.

## Test Cases
Unit/service/API/permission tests plus frontend tests where UI is touched.

## Visual Acceptance Criteria
Match the existing prototype patterns and include loading, empty, error, unauthorized, validation, and success states where relevant.

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
