# Ralph Handoff

## Last Run
2026-07-05_200043_normal_run

## Current Status
Slice `003G-dashboard-task-summary-api` completed successfully.

Architecture review is due before the next implementation slice: `.ralph/state.json` now has
`slices_completed_since_architecture_review: 4` and `architecture_review_due: true`.

## What Completed
- Added protected `GET /api/v1/dashboard/`.
- Response shape:
  - `data.role_context`
  - `data.cards[]` with `code`, `label`, `count`, `link`
  - `data.tasks[]`
- Supported role contexts:
  `credit_manager`, `sanction_committee`, `compliance`, `treasury`, and `management`.
- Current shell behavior:
  - all card counts are `0`;
  - tasks are `[]`;
  - no borrower/member/loan-account sensitive values are returned;
  - no downstream loan/compliance/treasury/management calculations were invented.
- Permission handling:
  - endpoint requires session-bound bearer auth;
  - read permission is `management_readonly` per A-023;
  - missing/revoked tokens return `401`;
  - authenticated users without `management_readonly` return `403`.
- Validation:
  - no query parameters are supported;
  - any query parameter returns standard `400 VALIDATION_ERROR`.
- Audit:
  - dashboard reads do not write `AuditLog` rows.
- Seed/catalogue update:
  - `management_readonly` is seeded and granted to dashboard role contexts;
  - `management_viewer` now has dashboard-summary access;
  - the guarded local/demo zero-permission user moved to role `it_head`.

## Working Docs Updated
- `docs/working/API_CONTRACTS.md`: dashboard endpoint contract, role contexts, zero-count shell,
  permission assumption, audit behavior, and deferrals.
- `docs/working/ASSUMPTIONS.md`: A-023 for dashboard permission/context handling and A-007
  cross-reference correction.
- `docs/working/digests/epic-003-audit-documents-config.md`: 003G implementation note for 003H.
- `docs/working/digests/epic-002-platform-auth.md`: note that `management_viewer` is no longer the
  demo zero-permission role after A-023.
- `docs/slices/003G-dashboard-task-summary-api.md`: marked Complete.
- `docs/slices/003H-dashboard-task-ui-wiring.md`: sharpened with exact 003G fields, contexts, and
  permission behavior.
- `docs/slices/003IA-notifications-center-ui-wiring.md`: sharpened to wait for 003I and keep
  dashboard tasks separate from notifications.

## Evidence
See `.ralph/runs/2026-07-05_200043_normal_run/`:
- `execution-plan.md`
- `evidence/terminal-logs/red-dashboard-api-tests.log`
- `evidence/terminal-logs/red-dashboard-catalogue-test.log`
- `evidence/terminal-logs/green-dashboard-api-tests.log`
- `evidence/terminal-logs/green-dashboard-catalogue-test.log`
- `evidence/terminal-logs/green-dashboard-seed-regression-tests.log`
- `evidence/terminal-logs/backend-check.log`
- `evidence/terminal-logs/backend-tests.log`
- `evidence/terminal-logs/backend-makemigrations-check.log`
- `evidence/terminal-logs/backend-coverage.log`
- `evidence/terminal-logs/frontend-typecheck.log`
- `evidence/terminal-logs/frontend-lint.log`
- `evidence/terminal-logs/frontend-tests.log`
- `evidence/terminal-logs/frontend-build.log`
- `evidence/api-responses/dashboard-api-response.txt`

## Current Blocker
None.

## Next Recommended Action
Run architecture review by cadence. After review, the next implementation slice is
`003H-dashboard-task-ui-wiring`.

Notes for `003H`:
- Use `docs/working/API_CONTRACTS.md` and the 003G digest note before opening large source docs.
- Wire the existing dashboard UI to `/api/v1/dashboard/`; do not add new styling or components.
- The backend currently returns `tasks: []`, so the frontend should use the existing empty-state
  pattern.
- Do not assume `management_viewer` is zero-permission; the neutral demo user is now `it_head`.
