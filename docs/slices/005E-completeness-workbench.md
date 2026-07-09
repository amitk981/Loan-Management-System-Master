# Slice 005E: Completeness Workbench

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
- 005D

## Prior Slice Facts
- 005B implemented `draft -> submitted`; submitted applications remain editable only through
  future controlled workflow actions, not direct draft `PATCH`.
- 005C confirmed source behavior: the official `LO...` reference is generated only after all
  mandatory completeness checks pass. 005C exposed
  `POST /api/v1/loan-applications/{loan_application_id}/generate-reference/` as the narrow
  completeness-pass transition, created the `system_sequences` and
  `loan_request_register_entries` tables, and recorded A-037 for the `reference_generated` status
  vocabulary.
- 005D provides `application_documents` metadata and a derived checklist foundation. 005E must
  build on those records instead of inventing document facts, re-uploading documents, or duplicating
  file/storage behavior.
- 005D concrete contract:
  - `GET/POST /api/v1/loan-applications/{loan_application_id}/application-documents/`
  - `POST /api/v1/application-documents/{application_document_id}/verify/`
  - `GET /api/v1/loan-applications/{loan_application_id}/document-checklist/`
  - `POST /api/v1/loan-applications/{loan_application_id}/document-checklist/refresh/`
- 005D checklist item codes that 005E must evaluate as mandatory before reference generation:
  `loan_application_form`, `borrower_pan`, `borrower_aadhaar_ovd`, `nominee_pan`,
  `nominee_aadhaar_ovd`, `share_certificate_copy`, `land_document_7_12`, `crop_plan`, and
  `six_month_bank_statement`. `cancelled_cheque` may exist as application-document metadata but is
  not required for the application-stage checklist.
- 005D upload creates versioned metadata rows (`submission_status = submitted`,
  initial `verification_status = pending`), verification supports `pending`, `verified`, and
  `rejected`, and duplicate document type/party uploads preserve history by creating a new version
  row. 005E should use the latest version per mandatory item and treat only `verified` as complete
  unless a source pass finds a stronger accepted-status mapping.
- 005D audit actions are `applications.application_document.attached` and
  `applications.application_document.verified`, both metadata-only. 005E completeness audit
  payloads must continue to omit raw file bytes, storage keys, checksums, full PAN/Aadhaar/bank
  values, encrypted tokens, and hashes.
- A-039 records that 005D checklist refresh is currently read-derived with no persisted checklist
  rows. If 005E adds persisted completeness decision/check history, keep it metadata-only and
  source-backed; do not reinterpret refresh as a mutating checklist update without documenting the
  source-backed permission/side effects.
- 005C2 should already enforce object-level access for loan application detail/actions. 005E must
  reuse that same application object-access boundary for workbench reads and completeness actions.
- Concretely, 005C2 exposed `applications.services.evaluate_application_object_access(...)` with
  created/received actors as current owner facts and `credit_manager` access only after the
  application reaches `current_stage = credit_assessment`. Completeness workbench reads/actions
  must preserve `403 PERMISSION_DENIED` for missing global permission and
  `403 OBJECT_ACCESS_DENIED` for same-permission actors outside object scope.
- Use `docs/working/digests/epic-005-application-intake.md` before reopening large source docs.

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
Completeness workbench only if the slice remains full-stack after source/code review; otherwise
backend/API first. Closest prototype reference: `sfpcl-lms/src/pages/applications/*`.

## Frontend Scope
If implemented in 005E, reuse only existing page/table/card/badge/modal patterns per
`docs/working/FRONTEND_DESIGN_RULES.md`. Do not redesign the application detail screen. Show the
submitted application facts, checklist rows, pass/fail actions, validation errors, and success
state from the real backend; no new mock data.

## Backend/API Scope
Implement the named backend/API capability only.

Concrete 005E scope:
- Add a completeness workbench/read endpoint for submitted applications, likely
  `GET /api/v1/loan-applications/{loan_application_id}/completeness-check/`, returning application
  summary, required checklist items from 005D, item statuses, missing/deficient reasons where
  available, and whether reference generation is currently allowed.
- Add a pass action that verifies all mandatory S12 checklist items are complete/verified and then
  invokes the existing 005C reference-generation service exactly once. Do not duplicate sequence or
  register logic.
- Add a fail/return-with-deficiency placeholder only if source/API sections make it narrow enough;
  otherwise defer deficiency creation/resolution to 005F and return validation errors listing
  incomplete checklist item codes.
- Do not implement eligibility, loan limit, appraisal note creation, sanction, disbursement,
  member-portal deficiency response, or rejection-note generation in 005E.

## Database/Model Impact
Non-destructive model/migration changes for this capability, if needed.

Expected model impact:
- Prefer using 005D checklist/application-document metadata plus existing `loan_applications`
  fields. Add a table only if needed to persist completeness decisions/check history; keep it to
  one migration and store metadata/status/reason facts only.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Apply the role and object-access rules from `docs/source/auth-permissions.md`; classify unknown access as approval-required.

Use `applications.loan_application.complete_check` for mutating completeness decisions. Read-only
workbench data should require `applications.loan_application.read` plus the 005C2 object-access
boundary. Do not invent a new completeness permission code.

## Audit Requirements
Record audit/workflow events for critical create/update/approval/access actions.

## Validation Rules
Enforce source-doc business rules and block invalid state transitions.

Specific validation to cover:
- Unknown applications return standard `404 NOT_FOUND`.
- Draft applications cannot pass completeness or generate references.
- Applications that already have `application_reference_number` or a loan request register entry
  cannot pass completeness again.
- Completeness pass is blocked until all mandatory S12/005D checklist items are present and
  verified/accepted. Return item-level errors rather than silently generating a reference.
- The item-level error payload should name the failing `document_type` codes from the 005D checklist
  and distinguish at least missing metadata from non-verified/rejected latest metadata, without
  exposing sensitive identity or file-storage values.
- Completeness pass must call the existing
  `applications.services.generate_reference_after_completeness_pass(...)` service rather than
  writing sequence/register/application-reference facts directly.
- Failed validation must not create partial sequence values on the application, register rows,
  workflow events, or audit rows.
- Preserve sensitive-data boundaries: responses/audits must not include PAN, Aadhaar, full bank
  account values, token values, hashes, or raw file bytes.

## Test Cases
Unit/service/API/permission tests plus frontend tests where UI is touched.

Minimum regression tests:
- Workbench read for a submitted application returns checklist status and `can_generate_reference`
  false until mandatory items pass.
- Completeness pass with all mandatory items complete calls the 005C path and returns the generated
  `LO...` reference plus register summary.
- Completeness pass with missing/rejected mandatory items returns `400 VALIDATION_ERROR` with item
  codes and creates no sequence/register/audit/workflow side effects.
- Draft and duplicate/reference-generated applications return `409 INVALID_STATE_TRANSITION` for
  completeness pass.
- Users without read/complete-check permissions receive `403 PERMISSION_DENIED`.
- Same-permission users outside the 005C2 object scope receive `403 OBJECT_ACCESS_DENIED`, and
  denials create no completeness audit rows, workflow events, register rows, references, or visible
  sequence advancement.

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
