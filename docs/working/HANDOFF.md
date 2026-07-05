# Ralph Handoff

## Last Run
2026-07-05_204654_normal_run

## Current Status
Slice `003G2-dashboard-internal-auditor-access-regression` completed successfully. The 003G
catalogue/dashboard mismatch for `internal_auditor` is fixed: the role now holds `management_readonly`,
so `GET /api/v1/dashboard/` returns its documented `role_context: "compliance"` shell instead of `403`.

## What Completed
- Diagnosed: `dashboard.services._ROLE_CONTEXTS` maps `internal_auditor -> "compliance"` and the
  endpoint gates on `management_readonly`, but `identity/catalogue.ROLE_PERMISSIONS` never granted it.
- TDD red-first: added a dashboard-API regression (seeded internal auditor -> `200` + compliance shell)
  and a `_ROLE_CONTEXTS` consistency invariant; both failed (`403` / missing permission), then passed
  after the fix. Red/green logs saved.
- Fix (source-backed by A-023 / `auth-permissions.md` §19.1): added `management_readonly` to the
  `internal_auditor` seed links. No contract, schema, or migration change.
- Consistency test now ties the seed to `_ROLE_CONTEXTS` so this class of gap fails the build in future.

## Working Docs Updated
- `docs/working/ASSUMPTIONS.md`: A-023 clarified that the internal_auditor grant is now realised
  (no decision reversal).
- `docs/working/digests/epic-003-audit-documents-config.md`: appended a 003G2 correction note.
- `docs/slices/003G2-...md`: Status -> Complete, checklist ticked.
- `.ralph/state.json`, `.ralph/progress.md`: updated.

## Evidence
See `.ralph/runs/2026-07-05_204654_normal_run/`:
- `execution-plan.md`, `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, `final-summary.md`
- `evidence/terminal-logs/backend-tests-red.log` (3 failing) and `backend-tests-green.log` (3 passing)
- `evidence/terminal-logs/backend-check.log`, `backend-tests.log`, `backend-makemigrations-check.log`,
  `backend-coverage.log`
- `evidence/terminal-logs/frontend-typecheck.log`, `frontend-lint.log`, `frontend-tests.log`,
  `frontend-build.log`
- `evidence/terminal-logs/git-diff-check.log`, `protected-path-scan.log`

## Current Blocker
None.

## Next Recommended Action
Run `003H-dashboard-task-ui-wiring`. Its 003G2 dependency is satisfied.

Notes for `003H`:
- Use `docs/working/API_CONTRACTS.md` and the 003G/003G2 digest notes before opening large source docs.
- Wire the existing dashboard UI (`sfpcl-lms/src/pages/Dashboard.tsx`) to `GET /api/v1/dashboard/`;
  no new styling or components (FRONTEND_DESIGN_RULES).
- Backend returns `role_context`, zero-count `cards[]`, and `tasks: []`; use the existing empty-state
  pattern for tasks and render the source-named cards with their counts (all `0` today) and links.
- Roles reaching the dashboard now include `internal_auditor` (compliance context). The neutral
  zero-permission demo user is `it_head`; do not assume `management_viewer` is zero-permission.
