# Slice 003C: Document Metadata and Storage Adapter

## Status
Not Started

## Parent Epic
Epic 003: Audit, Documents, Config, and Dashboard Foundation
Epic file: `docs/epics/003-audit-documents-config-foundation.md`

## Goal
Deliver the generic document-file metadata foundation and local storage adapter for uploaded files,
without building loan-document/checklist workflows yet.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 003B

## Source References
- docs/source/implementation-roadmap.md sections 10, 20-22
- docs/source/api-contracts.md sections 26, 39, 41, 42-43
- docs/source/data-model.md document/config/audit tables
- docs/source/component-spec.md
- docs/source/design-system.md

## Prototype Reference
- sfpcl-lms/src/pages/Dashboard.tsx
- sfpcl-lms/src/pages/tasks/TaskInbox.tsx
- sfpcl-lms/src/components/loan/AuditTimeline.tsx
- sfpcl-lms/src/components/loan/DocumentPackModal.tsx

## Screens Involved
None directly.

## Frontend Scope
None for this slice, except updating frontend documentation or fixtures if required by tests.

## Backend/API Scope
1. Add a `documents` backend app (or the established local equivalent) with a `DocumentFile`
   model matching `docs/source/data-model.md` §16.1: `document_id`, `file_name`,
   optional `file_extension`, optional `mime_type`, optional `file_size_bytes`,
   `storage_provider`, `storage_key`, optional `checksum_sha256`, nullable
   `uploaded_by_user`, `uploaded_at`, indexed `sensitivity_level`, and optional
   `retention_until_date`.
2. Add a small storage adapter interface plus local filesystem implementation for test/dev
   storage. Store file bytes out of the database; store only metadata and object key in
   `document_files`.
3. Add `POST /api/v1/document-files/` (`multipart/form-data`) from `api-contracts.md` §26.1
   with required fields `file`, `document_category`, `sensitivity_level`; optional
   `related_entity_type` and `related_entity_id`.
4. Return standard success envelope data with `document_id`, `file_name`, `mime_type`,
   `file_size_bytes`, `sensitivity_level`, and `uploaded_at`.
5. Keep this slice generic: do not create `loan_documents`, document checklists, download
   URLs, template generation, signature, stamp, or notarisation workflows.

## Database/Model Impact
Exactly one non-destructive migration is expected for `document_files`. Do not modify
existing audit/workflow/tracer migrations.

## API Contracts
Update `docs/working/API_CONTRACTS.md` with the implemented upload request/response,
validation errors, storage-provider behavior, and local adapter limits.

## Permissions
Require session-bound bearer auth. If the exact upload permission is not already present
in the seeded catalogue, do not invent a business grant; use the narrowest existing
document-related permission if present, otherwise record the source gap in
`docs/working/ASSUMPTIONS.md` and gate on a clearly named test-local permission only for
tests until the catalogue slice defines production grants.

## Audit Requirements
Successful uploads must write an `AuditLog` row for document upload using the actor,
`entity_type = "document_file"`, `entity_id = document_id`, and new-value metadata that
does not include raw file bytes.

## Validation Rules
- Missing `file`, `document_category`, or `sensitivity_level` returns standard
  `400 VALIDATION_ERROR` with `field_errors`.
- `sensitivity_level` is limited to source values: `public`, `internal`, `confidential`,
  `restricted` (case-normalize or reject consistently and document the choice).
- `related_entity_id`, when supplied, must be UUID.
- Compute and persist SHA-256 checksum for uploaded bytes.

## Test Cases
- Backend TDD red/green: upload API fails before `DocumentFile` service/model exists.
- Service: local adapter stores bytes outside the database and returns stable
  `storage_provider`, `storage_key`, `checksum_sha256`, and metadata.
- API: authenticated upload succeeds and response matches §26.1.
- API validation: missing file/required fields, invalid sensitivity, and invalid
  `related_entity_id` return `400 VALIDATION_ERROR`.
- Permission regression: unauthenticated request returns `401`; no-permission actor
  returns `403` without file/metadata/audit writes.
- Audit regression: successful upload writes exactly one document-upload audit row.

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
