# Slice 005F: Deficiency Creation and Resolution

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
- 005E

## Prior Slice Facts
- 005E added derived completeness workbench/read and pass endpoints:
  `GET /api/v1/loan-applications/{loan_application_id}/completeness-check/` and
  `POST /api/v1/loan-applications/{loan_application_id}/completeness-check/pass/`.
- 005E pass blocks until the latest 005D metadata row for every mandatory application-stage
  checklist code is `submitted` and `verified`, then delegates to
  `applications.services.generate_reference_after_completeness_pass(...)`.
- 005E validation failures already return item-level document codes with `missing_metadata` or
  `not_verified` reasons and create no sequence/register/audit/workflow side effects.
- 005F must build deficiency records/actions from those completeness failures instead of
  duplicating checklist derivation, document upload/storage behavior, or reference generation.

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

Concrete 005F scope:
- Add a narrow "return with deficiencies" action for submitted applications that records
  deficiency items selected from the 005E blocking checklist/application facts.
- Add list/read endpoints for deficiencies linked to a loan application so staff and later portal
  slices can display what must be corrected.
- Add a resolution/close action only if source/API review finds enough exact fields and state
  transitions; otherwise create the data model and staff return action, then defer borrower
  response/resubmission to member-portal slices.
- Do not implement rejection-note generation, eligibility, loan limit, appraisal, sanction,
  disbursement, or portal document re-upload UI in this slice.

## Database/Model Impact
Non-destructive model/migration changes for this capability, if needed.

Expected model impact:
- A deficiency table linked to `loan_applications`, with item code/type, reason/category, remarks,
  status, raised/resolved actor stamps, and metadata-only audit fields. Keep to one migration.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Apply the role and object-access rules from `docs/source/auth-permissions.md`; classify unknown access as approval-required.

Use existing `applications.loan_application.complete_check` for the staff action that returns a
submitted application with completeness deficiencies unless source review finds a narrower
permission. Read endpoints should require `applications.loan_application.read`. Reuse
`applications.services.evaluate_application_object_access(...)`.

## Audit Requirements
Record audit/workflow events for critical create/update/approval/access actions.

## Validation Rules
Enforce source-doc business rules and block invalid state transitions.

Specific validation to cover:
- Unknown applications return `404 NOT_FOUND`.
- Missing global permission returns `403 PERMISSION_DENIED`.
- Same-permission actors outside object scope return `403 OBJECT_ACCESS_DENIED` with no deficiency,
  audit, workflow, register, reference, or sequence side effects.
- Draft or already-reference-generated applications cannot be returned for completeness
  deficiencies unless source review finds a documented post-reference deficiency flow.
- Deficiency item codes must correspond to the 005E/005D blocking checklist facts or other
  source-backed S12 mandatory field facts; do not accept arbitrary free-form item codes as the
  only structured record.
- Returning for deficiencies must not generate an `LO...` reference, create a loan request register
  row, or advance to credit assessment.

## Test Cases
Unit/service/API/permission tests plus frontend tests where UI is touched.

Minimum regression tests:
- Submitted application with missing/rejected mandatory items can be returned with deficiency items
  and metadata-only audit/workflow evidence.
- Attempting to return an application with no selected/source-backed deficiency items returns
  `400 VALIDATION_ERROR`.
- Draft/reference-generated applications return `409 INVALID_STATE_TRANSITION`.
- Permission and object-scope denials create no deficiency rows or success audit/workflow events.
- Deficiency responses do not expose PAN, Aadhaar, full bank account values, storage keys,
  checksums, encrypted tokens, hashes, or raw file bytes.

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
