# Digest — Epic 003: Audit, Documents, Config, and Dashboard Foundation

Source extracts opened during 002I queue sharpening. `docs/source/` remains authoritative.

## Audit Foundation Extracts
- `docs/source/technical-architecture.md` §17.4 says audit logs should capture login/logout, failed login, member create/update, sensitive field view, document upload/download/verification, application submission, eligibility and loan-limit calculations, appraisal submission, approvals, rejection notes, checklist approvals, security custody movements, SAP code confirmation, disbursement initiation/authorisation, repayment posting/allocation, interest capitalisation, default/recovery, NOC, security return, configuration changes, and user/role permission changes.
- `docs/source/api-contracts.md` §42.1 defines `GET /api/v1/audit-logs/?entity_type=loan_application&entity_id=uuid`. Response items include `audit_log_id`, `actor{user_id, full_name}`, `actor_type`, `action`, `entity_type`, `entity_id`, `old_value`, `new_value`, `ip_address`, and `created_at`.
- `docs/source/api-contracts.md` §42.2 defines `GET /api/v1/workflow-events/?entity_type=loan_application&entity_id=uuid`.
- `docs/source/api-contracts.md` §42.3 defines `GET /api/v1/version-histories/?versioned_entity_type=loan_policy_config&versioned_entity_id=uuid`.

## Sharpened 003A Requirements
- Build only the audit-log read API over the existing `identity.AuditLog` model; do not create a second audit table.
- Add `GET /api/v1/audit-logs/` with filters `entity_type`, `entity_id`, and `actor_user_id`; invalid UUID filters return standard `400 VALIDATION_ERROR`.
- Return newest-first top-level pagination and use the 002J contract harness for success/error/pagination assertions.
- Map current model values to the §42.1 response item fields, including `old_value`/`new_value` even if stored as `old_value_json`/`new_value_json`.
- Current schema check during architecture review `2026-07-04_190302`: `identity.AuditLog.actor_user` is nullable. 003A should serialize no-actor/system rows as `actor: null` and test that path.
- Require session-bound bearer auth and existing `audit.audit_log.read`; do not invent `reports.audit.read`.
- No update/delete audit endpoints; preserve append-only behavior.
- IMPLEMENTED 2026-07-04 (`2026-07-04_202830_repair`): `GET /api/v1/audit-logs/` delivered
  via `identity/modules/audit_log.py` (service boundary) + `identity/audit_views.py` (thin
  view). Item shape, `actor: null` for system rows, `old_value`/`new_value` mapping, filters
  (`entity_type`/`entity_id`/`actor_user_id`), unknown-param and invalid-UUID → 400,
  newest-first pagination, and the `audit.audit_log.read` gate are all test-covered
  (`tests/test_audit_logs_api.py`, 12 tests). Contract in `API_CONTRACTS.md`; defaults in
  ASSUMPTIONS A-017. This is the pattern 003B should mirror for workflow-events read.

## Sharpened 003B Requirements
- `docs/source/api-contracts.md` §42.2 defines `GET /api/v1/workflow-events/?entity_type=loan_application&entity_id=uuid`; read access should use existing `audit.workflow_event.read`.
- Architecture review found 002EX drift: `sfpcl_credit/tracer.models.WorkflowEvent` already owns `db_table = "workflow_events"`. 003B must not create a second table with the same name.
- Prefer relocating ownership of the existing table to the canonical foundation model/service and repointing `sfpcl_credit/tracer/services.py::_record_event`; if migration-safe relocation is not practical, rename the tracer copy to `tracer_workflow_events` and create canonical `workflow_events` fresh in the same slice.
- Add a small internal `record_workflow_event(...)` interface that accepts explicit actor/workflow/entity/state/action/metadata facts and contains no loan eligibility, sanction authority, money, or document-completeness business rules.
- Preserve tracer regressions: seven successful tracer transitions still write seven workflow events and seven `AuditLog` rows; `makemigrations --check`, clean `migrate`, and full backend tests must remain green.
- Current tracer schema check during architecture review `2026-07-04_190302`: tracer `WorkflowEvent` fields are `workflow_event_id`, `workflow_name`, `entity_type`, `entity_id`, `from_state`, `to_state`, `triggered_by_user`, `trigger_reason`, and `created_at`; tracer API action payloads expose `workflow_event_id`. 003B should preserve that response field while moving persistence behind the canonical workflow-event service.
- IMPLEMENTED 2026-07-05 (`2026-07-05_083910_normal_run`): canonical model ownership moved to
  `sfpcl_credit.workflows.WorkflowEvent` with state-only migrations over the existing physical
  `workflow_events` table. `record_workflow_event(...)` writes canonical rows; tracer lifecycle
  writes through it and still returns `workflow_event_id`. `GET /api/v1/workflow-events/` is
  protected by `audit.workflow_event.read`, supports `entity_type`/`entity_id` filters, standard
  pagination, invalid UUID/unknown-param 400s, and newest-first ordering. Contract in
  `API_CONTRACTS.md`; defaults in ASSUMPTIONS A-018.

## Document Foundation Extracts
- `docs/source/data-model.md` §16.1 defines `document_files` as the central file metadata table:
  `document_id` UUID PK, `file_name`, optional `file_extension`, optional `mime_type`, optional
  `file_size_bytes`, `storage_provider`, `storage_key`, optional `checksum_sha256`,
  nullable `uploaded_by_user_id`, `uploaded_at`, indexed `sensitivity_level`, and optional
  `retention_until_date`.
- `docs/source/api-contracts.md` §26.1 defines `POST /api/v1/document-files/` multipart upload
  with required `file`, `document_category`, `sensitivity_level`; optional `related_entity_type`
  and `related_entity_id`; response data includes `document_id`, `file_name`, `mime_type`,
  `file_size_bytes`, `sensitivity_level`, and `uploaded_at`.
- `docs/source/api-contracts.md` §26.2 defines `GET /api/v1/document-files/{document_id}/download/`
  with either signed URL response `{download_url, expires_at}` or native stream.
- Existing digest audit extract from `technical-architecture.md` §17.4 says document upload,
  download, and verification actions should be audit-logged.
- `docs/source/data-model.md` §16.3 links downstream `loan_documents.document_id` to generated or
  uploaded `document_files`, but 003C should not create `loan_documents`; keep 003C to generic
  document metadata + storage adapter.
