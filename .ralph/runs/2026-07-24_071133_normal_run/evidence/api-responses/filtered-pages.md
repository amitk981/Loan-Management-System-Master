# Audit Explorer Filtered-Page Evidence

The focused API suite exercised these requests through Django's public HTTP boundary:

```text
GET /api/v1/audit-logs/?created_from=2026-07-24&created_to=2026-07-24
  &actor_user_id=<auditor UUID>&role_code=internal_auditor
  &entity_type=loan_application&entity_id=<application UUID>
  &action=approvals.exception.approved&module=approvals
  &exception=true&approval=true

GET /api/v1/workflow-events/?created_from=2026-07-24&created_to=2026-07-24
  &actor_user_id=<auditor UUID>&workflow_name=approval_exception
  &entity_type=loan_application&entity_id=<application UUID>
  &to_state=approved&exception=true&approval=true

GET /api/v1/version-histories/?created_from=2026-07-24&created_to=2026-07-24
  &author_user_id=<auditor UUID>&versioned_entity_type=loan_policy_config
  &versioned_entity_id=<configuration UUID>&approval=true

GET /api/v1/audit-logs/?application_reference=APP-AUD-012D
```

Each response was asserted as a standard successful list envelope with one matching item and
`pagination.total_count = 1`. The audit response projected retained actor role/team, reason,
outcome, request ID, module, and linked record. Its raw PAN, bank-account, access-token, and
unrestricted-request-body fixture values were absent and replaced with `[REDACTED]`. The version
response likewise redacted Aadhaar and cheque fixture values.

Evidence:

- `../terminal-logs/audit-explorer-green.log`
- `../terminal-logs/workflow-explorer-green.log`
- `../terminal-logs/version-explorer-green.log`
- `../terminal-logs/reference-filter-green.log`
- `../terminal-logs/final-focused-regression-2.log`

The 40-row PERF-010 representative test fixed every timestamp to the same value, asserted the UUID
descending tie-breaker, a 20-row first page with `has_next = true`, and at most eight SQL queries.
That behavior passed in `final-focused-regression-2.log`.
