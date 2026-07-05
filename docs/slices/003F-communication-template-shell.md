# Slice 003F: Communication Template Shell

## Status
Not Started

## Parent Epic
Epic 003: Audit, Documents, Config, and Dashboard Foundation
Epic file: `docs/epics/003-audit-documents-config-foundation.md`

## Goal
Deliver the content-template metadata/API foundation for borrower and internal communication
templates, without sending email/SMS/letters or building the notification center UI.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 003E

## Source References
- docs/source/implementation-roadmap.md sections 10, 20-22
- docs/source/api-contracts.md section 39.1
- docs/source/data-model.md section 24.1
- docs/source/functional-spec.md M16-FR-004 and M18-FR-006
- docs/source/auth-permissions.md content-template risk/control notes
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
1. Add a `communications` backend app (or established local equivalent) with `ContentTemplate`
   matching `docs/source/data-model.md` §24.1:
   `content_template_id`, unique `template_code`, `template_name`, indexed `template_type`,
   optional indexed `language_code`, indexed `audience`, optional `subject_template`,
   required `body_template`, optional `variables_json`, indexed `approval_status`,
   `template_version`, required `effective_from`, and nullable `effective_to`.
2. Implement `docs/source/api-contracts.md` §39.1:
   - `GET /api/v1/content-templates/` list with standard pagination.
   - `POST /api/v1/content-templates/` create a content template.
   - `PATCH /api/v1/content-templates/{content_template_id}/` update a content template.
3. Do not implement `POST /api/v1/communications/send/`, communication delivery queues,
   SMTP/SMS adapters, delivery status retries, manual phone-call logging, borrower/loan
   communication attachment, notification center UI, or document-template APIs in this slice.
4. Trace M16-FR-004 (store communication templates by event) and M18-FR-006 (maintain
   notification templates) in the review packet. Explicitly defer M16-FR-001 through M16-FR-003
   and M16-FR-005 through M16-FR-007 unless a later slice scopes actual communication sends.

## Database/Model Impact
One non-destructive migration is expected for `content_templates`.
Do not modify existing audit/workflow/document/config migrations.

## API Contracts
Update `docs/working/API_CONTRACTS.md` with request/response shapes, filters/pagination,
validation errors, audit actions, and permission assumptions.

## Permissions
The source docs classify content-template changes as Medium risk owned by Communication /
Compliance, but the current seeded catalogue has no clean §12 content-template read/manage code
(A-007 records adjacent communication permission gaps). Do not silently grant broad access.
Before implementation, choose the narrowest source-backed permission handling, record it in
`ASSUMPTIONS.md`, and test:
- missing/revoked bearer token returns `401`;
- authenticated actor without the chosen permission returns `403`;
- writes do not occur on `403`.

## Audit Requirements
Create and update must write `AuditLog` rows with stable action names such as
`communications.content_template.created` and `communications.content_template.updated`.
Audit metadata should include template id/code/name/type, audience, approval status, version, and
effective dates, but not rendered borrower-specific message content.

## Validation Rules
- Required create fields: `template_code`, `template_name`, `template_type`, `audience`,
  `body_template`, `approval_status`, `template_version`, and `effective_from`.
- `language_code`, `subject_template`, `variables`, and `effective_to` are optional.
- `effective_from` must be a valid ISO date; `effective_to`, if supplied, must be a valid ISO date
  on or after `effective_from`.
- `variables` must be a JSON array of strings and should persist to `variables_json`.
- `approval_status` is limited to `draft` or `approved`.
- Duplicate `template_code` returns a standard validation error without an audit row.
- Unknown `content_template_id` returns standard `404 NOT_FOUND`.

## Test Cases
- Backend TDD red/green: content-template API fails before model/service exists.
- API: authenticated list returns standard pagination and §39.1 fields.
- API: create succeeds, persists variables, and writes audit.
- API: patch succeeds and writes audit.
- Validation: missing required fields, invalid dates, invalid variables shape, invalid
  approval status, duplicate `template_code`, and unknown id return standard envelopes.
- Permissions: unauthenticated/revoked requests return `401`; no-permission actors return `403`
  without content-template or audit writes.
- Security: response/audit never includes rendered borrower-specific merge output.

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
