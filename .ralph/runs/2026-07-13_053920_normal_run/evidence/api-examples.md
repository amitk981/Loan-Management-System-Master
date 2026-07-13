# Approval Configuration API Evidence

Create/supersede requests require `reason` and return a pending proposal (`status: pending`,
`version: 1`) while the active resolver remains unchanged.

Approve: `POST /api/v1/approval-configuration-proposals/{id}/approve/` with `{"version":1}`.
Reject: `POST /api/v1/approval-configuration-proposals/{id}/reject/` with
`{"version":1,"reason":"Policy evidence incomplete"}`.

Observed contract codes in the retained public tests: `VALIDATION_ERROR`,
`MAKER_CHECKER_VIOLATION`, `APPROVER_AUTHORITY_REQUIRED`, `STALE_VERSION`,
`TRANSITION_CONFLICT`, and `CONFIGURATION_CONFLICT`. Successful approval produces one effective
row, one VersionHistory whose author and approver differ, and one `config.changed` audit carrying
reason, proposal id, actor ids, and request id without configuration secrets.
