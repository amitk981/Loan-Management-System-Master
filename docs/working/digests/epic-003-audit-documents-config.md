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
- Require session-bound bearer auth and existing `audit.audit_log.read`; do not invent `reports.audit.read`.
- No update/delete audit endpoints; preserve append-only behavior.

## Sharpened 003B Requirements
- `docs/source/api-contracts.md` §42.2 defines `GET /api/v1/workflow-events/?entity_type=loan_application&entity_id=uuid`; read access should use existing `audit.workflow_event.read`.
- Architecture review found 002EX drift: `sfpcl_credit/tracer.models.WorkflowEvent` already owns `db_table = "workflow_events"`. 003B must not create a second table with the same name.
- Prefer relocating ownership of the existing table to the canonical foundation model/service and repointing `sfpcl_credit/tracer/services.py::_record_event`; if migration-safe relocation is not practical, rename the tracer copy to `tracer_workflow_events` and create canonical `workflow_events` fresh in the same slice.
- Add a small internal `record_workflow_event(...)` interface that accepts explicit actor/workflow/entity/state/action/metadata facts and contains no loan eligibility, sanction authority, money, or document-completeness business rules.
- Preserve tracer regressions: seven successful tracer transitions still write seven workflow events and seven `AuditLog` rows; `makemigrations --check`, clean `migrate`, and full backend tests must remain green.
