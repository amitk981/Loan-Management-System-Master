# Candidate Permission Check

- `sfpcl_credit/recovery/**`: allowed by `sfpcl_credit/**`.
- `sfpcl_credit/approvals/**`: allowed by `sfpcl_credit/**`.
- `sfpcl_credit/config/{settings.py,urls.py}`: allowed by `sfpcl_credit/**`.
- `sfpcl_credit/tests/**`: allowed by `sfpcl_credit/**`.
- `docs/working/{API_CONTRACTS.md,ASSUMPTIONS.md}` if required: allowed by
  `docs/working/**`.
- `.ralph/runs/2026-07-22_151342_normal_run/**`: allowed by `.ralph/runs/**`.

No candidate path matches `.ralph/permissions.json` `requires_approval` or `forbidden` entries.
The stricter Ralph protected list was also checked: no scripts, Ralph configuration/permissions,
agent instructions, source documents, decision policy, frontend rules, or Git metadata will be
edited.
