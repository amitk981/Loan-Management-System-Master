# Slice 005D: Application Document Checklist

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
- 005C

## Prior Slice Facts
- 005A created draft loan applications with optional member land/crop/bank/cancelled-cheque
  references and metadata-only masked responses.
- 005B implemented submit as `draft -> submitted`; submitted applications remain at
  `current_stage = initial_loan_request`, `completeness_status = not_started`, and formal
  references remain nullable until the reference/completeness owner.
- 005C confirmed formal `LO...` generation is source-backed after completeness pass, not submit.
  It added `POST /api/v1/loan-applications/{loan_application_id}/generate-reference/`, the
  `system_sequences` row for `loan_application_reference`, and one-to-one
  `loan_request_register_entries`. 005D must not call that endpoint; it prepares the
  application-document/checklist metadata that 005E can evaluate before reference generation.
- Use `docs/working/digests/epic-005-application-intake.md` before reopening large source docs.
- Epic 004/005 sensitive data boundaries remain binding: document/checklist responses and audits
  must not include full PAN, Aadhaar, bank-account numbers, encrypted token values, hashes, or raw
  file bytes.

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

Concrete 005D scope:
- Add application-document metadata support for submitted loan applications:
  `GET /api/v1/loan-applications/{loan_application_id}/application-documents/` and
  `POST /api/v1/loan-applications/{loan_application_id}/application-documents/`.
- Add application-document verification:
  `POST /api/v1/application-documents/{application_document_id}/verify/`.
- Add a document checklist read/refresh foundation:
  `GET /api/v1/loan-applications/{loan_application_id}/document-checklist/` and, only if still
  narrow enough, `POST /api/v1/loan-applications/{loan_application_id}/document-checklist/refresh/`.
- Store/checklist metadata only and link uploaded items to the existing `documents.DocumentFile`
  record by UUID where practical. Do not duplicate file bytes or introduce new storage behavior in
  005D.
- Required application document types from source: loan application form, borrower PAN, borrower
  Aadhaar/OVD for individual borrowers, nominee PAN, nominee Aadhaar/OVD, share certificate copy,
  land document / 7/12 extract, crop plan, and six-month bank statement. Cancelled cheque may be
  collected at application stage but is required before disbursement, so do not block 005D
  checklist completion on it unless source review adds a stronger rule.
- Do not implement deficiency creation/resolution, completeness pass/fail, eligibility, appraisal,
  sanction, disbursement, frontend document screens, or real file scanning in this slice.

## Database/Model Impact
Non-destructive model/migration changes for this capability, if needed.

Expected model impact:
- `application_documents` metadata table if not already present, linked to `loan_applications` and
  optionally to `documents.document_files`.
- Fields should cover `document_type`, `party_type`, optional `party_id`, `required_flag`,
  `submission_status`, `verification_status`, verifier actor/time, remarks, created/updated actor
  timestamps, and a stable UUID primary key.
- Optional checklist table/items only if the source-backed checklist cannot be represented from
  `application_documents` metadata within one slice. Keep this to one migration.

## API Contracts
Create or update the API contract for this capability.

## Permissions
Apply the role and object-access rules from `docs/source/auth-permissions.md`; classify unknown access as approval-required.

Use source-backed application/document permissions:
- Listing application documents/checklist: require `applications.loan_application.read` plus object
  access where available.
- Uploading application documents: require `applications.document.upload`.
- Verifying application documents: require `applications.document.verify`.
- If refresh is implemented as a mutating checklist action, use the narrowest source-backed
  checklist/document permission found during the source pass; if no exact permission exists, record
  the assumption and avoid inventing a new permission code.

## Audit Requirements
Record audit/workflow events for critical create/update/approval/access actions.

Specific audit requirements:
- Successful upload/metadata attach writes metadata-only audit including application ID, document
  type, party type/ID, document file ID, submission status, verification status, actor, request ID,
  IP, and user-agent.
- Successful verification writes metadata-only audit including old/new verification status and
  remarks. Do not include file content, OCR values, PAN/Aadhaar full values, tokens, hashes, or bank
  full numbers.
- Listing checklist/documents is read-only and should not write workflow events unless source
  review requires access audits.

## Validation Rules
Enforce source-doc business rules and block invalid state transitions.

Specific validation to cover:
- Reject unknown loan applications and unknown application-document IDs.
- Reject upload/attach for draft applications if source review confirms documents are collected
  only after submit; otherwise record the allowed draft behavior explicitly in assumptions.
- Require valid `document_type`, `party_type`, and file/document reference.
- Supported `party_type` values for this slice: `borrower`, `nominee`, and `witness`.
- Supported verification values: `pending`, `verified`, `rejected`; upload starts as submitted /
  pending-verification metadata.
- Duplicate document types should create a new version/history row or reject with a standard
  duplicate-state error; do not overwrite audit history.
- Verification must be possible only for submitted document metadata, not missing/pending
  placeholders.

## Test Cases
Unit/service/API/permission tests plus frontend tests where UI is touched.

Minimum regression tests:
- List/refresh checklist for a submitted application returns required source document item codes and
  pending statuses without sensitive identity/bank values.
- Upload/attach an application document persists metadata, links the existing document file, returns
  a standard envelope, and writes metadata-only audit.
- Verify an uploaded document changes verification status, stamps verifier/time, and writes
  metadata-only audit with old/new status.
- Unknown applications/document IDs return standard `404 NOT_FOUND`.
- Users without read/upload/verify permissions receive `403 PERMISSION_DENIED` and no writes.
- Duplicate upload/version behavior preserves history and never overwrites prior audit facts.

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
