# Slice 005B: Application Submit and Status Transition

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
- 005A

## Prior Slice Facts
- 005A should create/read/update draft loan applications only. 005B must depend on those persisted
  draft fields and must not reintroduce member-master mock data or duplicate the Epic 004 member
  subresource APIs.
- Epic 004 sensitive data boundaries remain binding: submit responses and audit/workflow metadata
  must not include full PAN, Aadhaar, full bank account numbers, protected token values, or hashes.
- Completeness, reference-number generation, document checklist verification, deficiency workflow,
  eligibility, loan limit, appraisal, sanction, disbursement, and payment initiation remain outside
  005B unless explicitly split into this slice later.

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

Concrete 005B scope:
- Add a submit action for 005A draft loan applications, such as
  `POST /api/v1/loan-applications/{application_id}/submit/`, using the existing state-machine guard
  foundation where practical.
- Permit only `draft -> submitted` (or the exact source-backed initial submitted status if 005A/005B
  source pass confirms a different canonical name). Do not generate final application/reference
  numbers in this slice unless source §19-21 explicitly says submit owns them; otherwise leave
  reference-number generation to 005C.
- Persist submitted actor/timestamp and return a standard envelope with the updated application
  status plus masked member/bank metadata only.
- Write metadata-only audit and workflow event entries for submit; no workflow events for failed
  validation beyond existing audit conventions unless the source docs require them.

## Database/Model Impact
Non-destructive model/migration changes for this capability, if needed.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Apply the role and object-access rules from `docs/source/auth-permissions.md`; classify unknown access as approval-required.

## Audit Requirements
Record audit/workflow events for critical create/update/approval/access actions.

## Validation Rules
Enforce source-doc business rules and block invalid state transitions.

Specific validation to cover:
- Reject submit for unknown application IDs.
- Reject submit when the application is not in draft status.
- Reject submit if source-required draft fields from 005A are missing, but do not invent
  completeness, eligibility, duplicate-bank, document, disbursement, payment, or appraisal blockers.
- Record any unresolved canonical submitted status name or permission mapping in
  `docs/working/ASSUMPTIONS.md` rather than inventing a business rule.

## Test Cases
Unit/service/API/permission tests plus frontend tests where UI is touched.

Minimum regression tests:
- Draft submit succeeds once, changes status, stamps submitted actor/time, and writes
  metadata-only audit/workflow evidence.
- Re-submitting or submitting a non-draft application returns a standard transition error envelope.
- User without the source-backed submit permission is denied.
- Submit response/audit/workflow metadata contains no full sensitive member or bank values.

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
