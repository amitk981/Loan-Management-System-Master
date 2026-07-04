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
- Require session-bound bearer auth and the narrowest existing source-backed audit/report/admin read permission; if no exact catalogue code exists, record the permission assumption instead of inventing a code.
- No update/delete audit endpoints; preserve append-only behavior.
