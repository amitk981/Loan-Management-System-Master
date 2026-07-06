# Slice 003I: Notification Adapter Shell

## Status
Complete

## Parent Epic
Epic 003: Audit, Documents, Config, and Dashboard Foundation
Epic file: `docs/epics/003-audit-documents-config-foundation.md`

## Goal
Deliver the first communication/notification adapter foundation over source `communications`
records: persist outbound communication metadata, render message snapshots from approved content
templates, and expose current metadata/list APIs without sending real email, SMS, courier, or
in-app notifications yet.

## User Value
Moves the platform one verifiable step closer to a working end-to-end lending system without broad module-sized changes.

## Depends On
- 003H

## Source References
- docs/source/api-contracts.md sections 39.2-39.3
- docs/source/data-model.md section 24.2
- docs/source/functional-spec.md M16-FR-001 through M16-FR-007 and notification matrix
- docs/source/screen-spec.md S04 notification categories/fields/actions
- docs/source/content-spec.md S04 notification fields/tabs and section 16 notification copy
- docs/source/auth-permissions.md communication/content-template risk notes
- docs/working/digests/epic-003-audit-documents-config.md communication extracts

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
1. Add a `Communication` model/table matching `docs/source/data-model.md` §24.2:
   `communication_id`, `related_entity_type`, `related_entity_id`, `recipient_party_type`,
   nullable `recipient_party_id`, nullable `recipient_address`, `channel`, nullable
   `content_template_id`, nullable `subject_snapshot`, required `body_snapshot`,
   nullable `sent_by_user_id`, nullable indexed `sent_at`, indexed `delivery_status`, nullable
   `acknowledgement_status`, and nullable `external_message_id`.
2. Implement `POST /api/v1/communications/send/` as a shell that validates the request from
   `api-contracts.md` §39.2, renders subject/body snapshots by substituting supplied `merge_data`
   into an approved `ContentTemplate`, persists the communication row, and returns metadata.
3. Do not send email, SMS, courier, hard-copy letters, or provider calls. For this shell,
   `delivery_status` should remain `pending` unless a source-backed adapter result exists.
4. Implement `GET /api/v1/communications/?related_entity_type=...&related_entity_id=uuid` from
   `api-contracts.md` §39.3 with standard pagination and strict query validation.
5. Keep in-app notification list/mark-read persistence out of this slice unless it can be expressed
   directly by the source `communications` table without inventing fields. `003IA` owns the
   Notifications Center UI and may require a later notification-specific model/API if §24.2 is not
   sufficient for S04 read/unread/action states.
6. Explicitly trace M16-FR-001 through M16-FR-007: this shell supports metadata/snapshot creation
   and delivery-status storage, but real channel delivery, manual phone-call reminders, and
   borrower/loan attachment beyond generic related-entity fields remain deferred unless implemented
   by source fields only.

## Database/Model Impact
One non-destructive migration is expected for `communications`. Do not alter the existing
`content_templates` schema from 003F unless a failing test proves a contract mismatch.

## API Contracts
Update `docs/working/API_CONTRACTS.md` with request/response shapes, pagination, validation,
delivery-status behavior, permission assumptions, and explicit no-real-send deferral.

## Permissions
The source catalogue gap from A-007/A-022 still applies: do not silently reuse broad report,
document-template, or config permissions. Choose the narrowest source-backed communication
permission handling, record it in `docs/working/ASSUMPTIONS.md`, and test `401`/`403`.

## Audit Requirements
Creating a communication snapshot must write one `AuditLog` row with metadata identifying the
related entity, recipient party, channel, template, and delivery status. Do not include full
rendered borrower message bodies in audit metadata unless source docs later require it.

## Validation Rules
- Required send fields: `related_entity_type`, `related_entity_id`, `recipient_party_type`,
  `channel`, `content_template_id`, and `merge_data`.
- `related_entity_id` and `recipient_party_id`, when supplied, must be valid UUIDs.
- `channel` must be one of the source channels represented in §24.2/functional matrix:
  `email`, `sms`, `phone`, or `courier` unless a source extract justifies another value.
- `content_template_id` must reference an approved template whose `effective_from/effective_to`
  window includes today; if exact effective-date semantics are ambiguous, record the assumption.
- All template variables declared in `ContentTemplate.variables_json` must be present in
  `merge_data`; extra merge keys should be rejected or ignored consistently and documented.
- Unknown list query parameters return standard `400 VALIDATION_ERROR`.

## Test Cases
- Backend TDD red/green: send/list communication API tests fail before model/service exists.
- API: send shell persists source §24.2 fields, body/subject snapshots, pending delivery status,
  and writes audit.
- API: list filters by `related_entity_type` and `related_entity_id`, uses standard pagination,
  rejects invalid UUIDs and unknown parameters.
- Validation: missing required fields, inactive/unapproved template, missing merge variables,
  invalid channel, invalid UUIDs, and unknown template return standard envelopes without writes.
- Permissions: unauthenticated/revoked requests return `401`; authenticated users without the
  chosen communication permission return `403` without communication or audit writes.
- Security: response and audit do not expose provider credentials, external secrets, or raw
  borrower-specific rendered bodies beyond the intended API response fields.

## Queue Sharpening Notes
- 003H now owns only the dashboard role-summary endpoint and still expects `tasks: []`; do not reuse
  `/api/v1/dashboard/` as a notification list or communication history endpoint.
- Keep 003I backend-only unless a failing contract test proves the existing frontend needs a fixture
  adjustment. The Notifications Center UI replacement remains 003IA.
- If `ContentTemplate.variables_json` contains variables not supplied in `merge_data`, fail the send
  shell before persisting `Communication` or `AuditLog`. If `merge_data` contains extra keys, choose
  one deterministic behavior, record it in `ASSUMPTIONS.md`, and test it.
- Save API examples for `POST /api/v1/communications/send/`, `GET /api/v1/communications/`, `401`,
  `403`, and validation failure in the run evidence folder.

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
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated, if needed
- [x] Database rules followed, if needed
- [x] Permissions tested, if needed
- [x] Audit events tested, if needed
- [x] Visual evidence saved, if frontend
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates
