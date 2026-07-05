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
- `docs/source/auth-permissions.md` endpoint map lists `POST /document-files/` under
  `documents.file.upload` and `GET /document-files/{id}/download/` under
  `documents.file.download` plus a sensitivity check. Restricted-file downloads should create a
  `documents.file.downloaded` audit event, and source implementation details for the full
  role/sensitivity matrix remain broader than 003D's generic download-link foundation.

## Configuration Foundation Extracts
- `docs/source/data-model.md` §25.1 defines `loan_policy_configs` with UUID PK,
  `policy_name`, `policy_version`, effective date range, duration/month/year settings,
  approval threshold, default scale of finance, share percentage, per-share cap, interest fields,
  re-KYC/retention/grace/extension settings, nullable `board_approval_reference`, and indexed
  `status` (`draft` / `active` / `retired`).
- `docs/source/data-model.md` §26.3 defines `version_histories` with UUID PK,
  `versioned_entity_type`, `versioned_entity_id`, `version_number`, `change_summary`,
  nullable author/reviewer/approver user FKs, nullable `board_approval_reference`,
  `effective_from`, nullable `effective_to`, and `created_at`.
- `docs/source/api-contracts.md` §41.1 defines loan-policy config endpoints:
  `GET /api/v1/config/loan-policy/`, `POST /api/v1/config/loan-policy/`,
  `PATCH /api/v1/config/loan-policy/{loan_policy_config_id}/`, and
  `POST /api/v1/config/loan-policy/{loan_policy_config_id}/activate/`, with the request fields
  mirrored from `loan_policy_configs`.
- `docs/source/api-contracts.md` §42.3 defines
  `GET /api/v1/version-histories/?versioned_entity_type=loan_policy_config&versioned_entity_id=uuid`.
- `docs/source/technical-architecture.md` §27 says major rule changes must be drafted, reviewed,
  approved, capture board approval reference where required, be effective-dated, versioned, and
  audit logged.
- `docs/source/auth-permissions.md` §12.13 provides `config.loan_policy.read`,
  `config.loan_policy.manage`, and `audit.version_history.read`; §31 says critical configuration
  changes require reason, effective dates, historical availability, and activation audit logs.
- `docs/source/functional-spec.md` M01-FR-001 says the system maintains one or more loan product
  configurations for SFPCL member lending. M01-FR-002 says each policy configuration stores
  effective date, version, approval authority, and Board approval reference. M01-FR-015 says policy
  activation must be blocked without required approval evidence.
- 003E should trace M01-FR-001, M01-FR-002, and M01-FR-015 directly. Functional requirements
  M01-FR-003 through M01-FR-014 cover eligibility parameters, share valuation, scale of finance,
  approval matrix, interest, charges, document-template/checklist rules, re-KYC, and compliance
  task frequencies; those should be explicitly deferred to their owning later slices unless 003E
  implements only neutral storage fields already in `loan_policy_configs`.
- IMPLEMENTED 2026-07-05 (`2026-07-05_191550_normal_run`): `sfpcl_credit.configurations` now owns
  `LoanPolicyConfig` (`loan_policy_configs`) and `VersionHistory` (`version_histories`) with one
  non-destructive migration. Implemented protected `GET/POST/PATCH/activate` loan-policy endpoints
  and protected `GET /api/v1/version-histories/`; list responses use standard pagination,
  mutations write `config.loan_policy.*` audit rows, activation writes `VersionHistory`, and
  activation requires `board_approval_reference` for M01-FR-015. A-021 records the source-silent
  prior-active retirement rule. M01-FR-003 through M01-FR-014 remain deferred; no eligibility,
  share valuation, scale-of-finance, approval matrix, interest, charge, document-template, re-KYC,
  or compliance-frequency calculations were implemented.

## Communication Template Foundation Extracts
- `docs/source/api-contracts.md` §39.1 defines content-template endpoints:
  `GET /api/v1/content-templates/`, `POST /api/v1/content-templates/`, and
  `PATCH /api/v1/content-templates/{content_template_id}/`. Create fields are
  `template_code`, `template_name`, `template_type`, `language_code`, `audience`,
  nullable `subject_template`, required `body_template`, `variables`, `approval_status`,
  `template_version`, and `effective_from`.
- `docs/source/data-model.md` §24.1 defines `content_templates` with UUID primary key,
  unique `template_code`, indexed `template_type`, optional indexed `language_code`,
  indexed `audience`, optional `subject_template`, required `body_template`, optional
  `variables_json`, indexed `approval_status` (`draft` / `approved`), `template_version`,
  required `effective_from`, and nullable `effective_to`.
- `docs/source/functional-spec.md` M16-FR-004 says the system stores communication templates by
  event; M18-FR-006 says it maintains notification templates. M16-FR-001 through M16-FR-003 and
  M16-FR-005 through M16-FR-007 cover sending email/SMS/letters, delivery status, manual calls, and
  attaching communications to borrower/loan records; defer those from 003F unless a later slice
  explicitly scopes send/list communication records.
- `docs/source/auth-permissions.md` risk table classifies content-template changes as Medium risk
  owned by Communication / Compliance. The current permission catalogue gap from A-007 still applies:
  source role details mention `communications.communication.create`, but no clean §12 catalogue code
  for content-template read/manage has been seeded yet. 003F must not silently grant broad access;
  it should either add a source-backed narrow permission with an assumption or defer write access
  until the catalogue gap is resolved.

## Sharpened 003F Requirements
- Build only the content-template metadata/API shell. Do not send communications, retry delivery,
  integrate SMTP/SMS, create notification center UI, or create borrower/loan communication records.
- Add a `communications` backend app (or established local equivalent) with `ContentTemplate`
  matching `data-model.md` §24.1. One non-destructive migration is expected.
- Implement §39.1 list/create/patch APIs using the standard envelopes and pagination harness.
- Validation defaults: `template_code`, `template_name`, `template_type`, `audience`,
  `body_template`, `approval_status`, `template_version`, and `effective_from` are required;
  `effective_to`, if supplied, must be on or after `effective_from`; `variables` must be a JSON
  array of strings; `approval_status` is limited to `draft` or `approved`.
- Audit create/update actions with stable action names such as `communications.content_template.created`
  and `communications.content_template.updated`; audit metadata should include template identifiers,
  type, audience, approval status, version, and effective dates, but not rendered borrower-specific
  message content.
- Because the source permission catalogue is incomplete for content-template management, 003F must
  explicitly record its chosen permission handling in `ASSUMPTIONS.md` and test `401`/`403` behavior.
