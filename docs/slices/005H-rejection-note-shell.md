# Slice 005H: Rejection Note Shell

## Status
Not Started

## Parent Epic
Epic 005: Loan Application Intake, Documents, Completeness, and Deficiencies
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal
Add the staff-side rejection-note metadata shell for applications that cannot proceed after intake
review, without implementing letter delivery, appraisal rejection, sanction rejection, or borrower
portal response behavior.

## User Value
Credit/finance staff can record a controlled, auditable rejection-note draft against an application
while preserving the intake workflow guarantees that references, registers, and downstream appraisal
state are only created by their owning slices.

## Depends On
- 005G2

## Prior Slice Facts To Preserve
- 005G2 closed the portal session/audit hardening finding. Old portal sessions now receive
  `401 INVALID_TOKEN` after `PortalAccount.status` stops being active, and the session is revoked
  with `portal_account_status_changed`. Keep staff rejection-note audit actions staff-scoped and
  do not reuse portal action names for internal staff work.
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
- Suspended portal accounts must not be able to reach staff rejection-note APIs through old portal
  sessions. Tests should assert `401 INVALID_TOKEN` for that old-token case; valid active portal
  tokens without staff permissions should still receive `403 PERMISSION_DENIED`.

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
- Staff Application Detail / intake review area
- Staff Application List status/action affordance, only if an existing action slot can be reused
- Borrower portal MP09/MP10 may read final/published rejection facts later, but portal delivery is
  out of scope for this slice

## Frontend Scope
- Prefer backend/API-only unless the existing staff Application Detail has a minimal existing action
  slot that can show rejection-note status without new styling.
- Do not add borrower portal rejection-note creation or response controls.
- If touched, preserve existing staff application page cards, status badges, action panels, loading,
  empty, error, unauthorized, validation, and success patterns.

## Backend/API Scope
- Add the smallest staff-side rejection-note shell needed by the source application workflow.
- Reuse existing `LoanApplication` state/object-access helpers where possible.
- If the source-backed rejection-note persistence model is absent, add only the narrow model needed
  for metadata fields and auditability; do not add appraisal, sanction, document-generation, or
  borrower-letter delivery behavior in this slice.
- Implement source API shell endpoints from the rejection section:
  - `POST /api/v1/loan-applications/{loan_application_id}/rejection-note/`
  - `POST /api/v1/loan-applications/{loan_application_id}/rejection-note/send/` only as a
    metadata/status transition if the source fields are clear; otherwise explicitly defer send and
    document the assumption.
- Rejection-note create/update must not call the completeness pass/reference-generation service and
  must not create `loan_request_register_entries`.
- If status changes are source-backed in the opened source pass, represent the rejected state with
  the existing `LoanApplication` status vocabulary; otherwise keep the application state unchanged
  and persist only rejection-note draft metadata.

## Database/Model Impact
- Add at most one non-destructive migration for `rejection_notes` if it is not already present.
- Persist only metadata needed for traceability: linked application, reason/category/message,
  current note status, created/updated/sent actors and timestamps where source-backed.
- Do not store PAN, Aadhaar, full bank-account values, raw document contents, encrypted values, or
  token/hash fields in rejection-note payloads or audit metadata.

## API Contracts
- Update `docs/working/API_CONTRACTS.md` with request/response examples, error envelopes, state
  rules, and side-effect guarantees.
- Responses must follow the standard envelope and include the application id, rejection-note id,
  note status, source-safe reason/message metadata, and timestamps only.

## Permissions
- Staff-only. Require the source-backed application read/object-access boundary plus the narrowest
  source-confirmed rejection/write permission available after reading the source sections.
- Borrower portal tokens must receive `403 PERMISSION_DENIED` for staff rejection-note actions.
- Same-permission staff outside the application object scope receive `403 OBJECT_ACCESS_DENIED`
  after global permission and `404` checks, matching 005C2/005D/005E/005F object-access ordering.

## Audit Requirements
- Create/update/send actions write metadata-only audit rows and workflow events only on success.
- Failed validation, permission denial, object denial, not-found, and invalid-state attempts create
  no rejection note, success audit row, workflow event, register row, reference, or sequence change.

## Validation Rules
- Reject unknown applications with `404 NOT_FOUND`.
- Reject same-permission staff outside the application object scope with `403 OBJECT_ACCESS_DENIED`
  and no audit/workflow side effects.
- Reject invalid state transitions without creating rejection metadata, audit rows, workflow
  events, register rows, references, or sequence advancement.
- Require a source-backed rejection reason/message field for create. Reject empty reason/message
  and unknown request fields with `400 VALIDATION_ERROR`.
- Keep `incomplete_returned` applications distinct from rejected applications; do not use the
  rejection-note shell to repeat-return deficiencies.

## Test Cases
- Staff with permission and object access can create a rejection-note draft for an eligible
  application and receives a metadata-only response.
- Missing permission returns `403 PERMISSION_DENIED`; same-permission out-of-scope staff returns
  `403 OBJECT_ACCESS_DENIED`.
- Borrower portal token cannot create/send rejection notes.
- A suspended portal account token cannot create/send rejection notes, receives
  `401 INVALID_TOKEN`, and cannot receive portal action availability through `/auth/me`.
- Invalid state and duplicate/create-after-send cases create no rejection note, audit, workflow,
  register, reference, or sequence side effects.
- Response/audit payloads do not contain PAN, Aadhaar, full bank account values, encrypted values,
  token hashes, or raw document contents.

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
