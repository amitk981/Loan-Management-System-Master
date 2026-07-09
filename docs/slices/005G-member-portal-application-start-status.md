# Slice 005G: Member Portal Application Start and Status

## Status
Not Started

## Parent Epic
Epic 005: Loan Application Intake, Documents, Completeness, and Deficiencies
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal
Wire the authenticated borrower/member application screens to real backend data: MP05 new
application start, MP06/MP08 draft/review submission path where supported by existing 005A/005B
APIs, MP09 my applications list, and MP10 application status.

## User Value
A logged-in member can start or resume their own draft application, submit it to SFPCL, and see
their own application status without staff assistance.

## Depends On
- 005FB

## Source References
- docs/source/implementation-roadmap.md section 11
- docs/source/api-contracts.md sections 19-21
- docs/source/data-model.md loan origination tables
- docs/source/screen-spec.md application screens
- docs/source/screen-spec-member-portal.md application screens

## Prototype Reference
- sfpcl-lms/src/pages/borrower/portal/applications/MP05_NewApplication.tsx
- sfpcl-lms/src/pages/borrower/portal/applications/MP09_MyApplications.tsx
- sfpcl-lms/src/pages/borrower/portal/applications/MP10_ApplicationStatus.tsx
- Existing staff application API/service patterns in sfpcl-lms/src/pages/applications/*

## Screens Involved
- MP05 New Application Start
- MP06/MP08 draft/review facts as represented by the current prototype flow
- MP09 My Applications
- MP10 Application Status

## Frontend Scope
- Replace mock application data in MP05/MP09/MP10 with real member-portal APIs.
- Preserve existing portal layout, cards, table/list patterns, badges, and spacing.
- Show submitted applications without an official `LO...` reference until completeness passes.
- Render returned-incomplete applications as borrower rectification work using
  `application_status = incomplete_returned`, not plain `submitted`.
- Include loading, empty, error, unauthorized, validation, draft-saved, submitted, and
  returned-incomplete states.

## Backend/API Scope
- Add member-scoped portal endpoints backed by the 005A/005B application services:
  - create/update/read own draft application using the authenticated `member_id` from 005FA;
  - submit own draft application to the existing `submitted` state;
  - list own applications for MP09;
  - read own application status for MP10.
- Do not accept client-supplied `member_id` as authority. The portal token’s `member_id` is the
  borrower scope.
- Do not expose staff completeness, reference-generation, return-with-deficiencies, or deficiency
  resolve actions to borrowers.
- Do not implement document upload/checklist, deficiency response/resubmission, rejection note,
  eligibility, appraisal, sanction, disbursement, or repayment behavior in this slice.

## Database/Model Impact
- Prefer reusing the existing `loan_applications` model. Add fields only if a required MP05 fact
  cannot be represented by the current 005A draft schema.

## API Contracts
- Update `docs/working/API_CONTRACTS.md` with the member-portal application endpoints and response
  examples. Responses must follow the standard envelope and avoid PAN, Aadhaar, full bank account
  numbers, encrypted values, token hashes, or raw document contents.

## Permissions
- Require an authenticated portal account with `portal_role = borrower_member` and matching
  `member_id`.
- Cross-member read/write attempts return `403 OBJECT_ACCESS_DENIED` and create no application,
  audit, workflow, register, reference, or sequence side effects.
- Staff users should continue to use existing staff application endpoints; do not broaden staff
  access through portal routes.

## Audit Requirements
- Draft create/update and submit must reuse existing metadata-only audit/workflow behavior where
  possible, with actor set to the linked portal user.
- Read-only list/status access does not need a new audit row unless existing service conventions
  already audit it.

## Validation Rules
- Draft save may remain incomplete, matching 005A.
- Submit requires the persisted 005B facts: member from portal scope, positive requested amount,
  declared purpose, and purpose category.
- Submitted applications are locked from direct draft editing.
- Official `LO...` reference remains nullable until staff completeness pass generates it.
- Returned deficiency applications remain `incomplete_returned`; resubmission from
  `incomplete_returned` is out of scope unless source-backed transition requirements are added.

## Test Cases
- Borrower can create, update, submit, list, and read status for their own application.
- Borrower cannot create/list/read/update/submit another member's application.
- Borrower token cannot call staff completeness/reference/deficiency-return APIs.
- Submitted application can appear with no official reference number.
- Returned-incomplete application displays borrower-facing rectification status without enabling
  staff repeat-return behavior.
- Frontend tests cover API mapping and loading/error/empty states for MP09/MP10.

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
