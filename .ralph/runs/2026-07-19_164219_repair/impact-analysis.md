# Impact Analysis

Selected slice: `CR-012-epic-009-playwright-evidence-is-incomplete`
Mode: repair

## Demonstrated failure

- The authoritative failure is
  `.ralph/runs/2026-07-19_163229_repair/evidence/terminal-logs/trusted-browser-acceptance-1.log`.
  The declared real-Django Playwright flow reaches
  `POST /api/v1/loan-accounts/{id}/disbursements/initiate/`, receives HTTP 400, and stops after five
  of the nine required screenshots. The earlier repair run reached the same endpoint with HTTP 200,
  so this repair must make the browser/API handoff deterministic and expose the exact Django error
  if it fails.

## Affected backend models, endpoints, and services

- Grep maps the guarded fixture owner to
  `sfpcl_credit/identity/management/commands/seed_epic_009_e2e_fixture.py` and its regression class in
  `sfpcl_credit/tests/test_seed_e2e_users.py`.
- The fixture creates deterministic synthetic users and owner evidence consumed by the real
  `/api/v1/auth/**`, `/api/v1/loan-accounts/**`, and `/api/v1/disbursement-workspaces/**` reads and
  by the initiation action URL projected from `sfpcl_credit/processes/disbursement_workspace.py`.
  The mutation is handled by `sfpcl_credit/disbursements/views.py` and the existing disbursement
  owner modules; no production model, endpoint, service, permission, or contract change is in scope.
- Backend blast radius includes the identity seed command, loan-account projection, workspace
  projection, initiation validation, source-bank governance, and readiness evidence. The repair will
  add a fixture regression that submits the exact projected action payload through Django and proves
  the isolated fixture reaches HTTP 200 before Playwright depends on it.

## Affected frontend screens, components, and routes

- The direct frontend owner is
  `sfpcl-lms/e2e/epic-009-staff-disbursement-closure.e2e.spec.ts`, exercising the existing Loan
  Accounts, SAP & Disbursement, Payment Authorisation, notifications, and safe-error routes.
- `sfpcl-lms/src/pages/disbursement/DisbursementHub.tsx` builds the initiation request through
  `sfpcl-lms/src/services/disbursementApi.ts`; these are inspected consumers, not production change
  targets. The repair must wait for their server-projected form values to be present before clicking
  and must retain the genuine Django response body on failure.
- Other browser contracts, including the existing 009I2 MP14 evidence flow, are outside the changed
  spec and remain regression surfaces only.

## Regression tests and validation

- Backend fixture module: extend the focused guarded Epic 009 seed regression to POST the exact
  workspace-projected fixed payload plus field defaults/comments and assert the real initiation
  endpoint returns `initiated / pending / pending`.
- Browser evidence module: retain the declared spec as the end-to-end regression, with explicit
  visible/value assertions immediately before submission and response diagnostics that identify a
  genuine Django validation failure. It must still capture nine fresh pairwise-distinct PNGs and a
  deterministic SHA-256 manifest.
- Run the focused backend seed test with
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python`, exact Playwright collection/static boundary checks,
  impacted frontend tests, typecheck, lint, and build. The orchestrator owns the authoritative two
  trusted browser executions and complete backend coverage gate.

## Frontend design compliance

No production UI, styling, colour, typography, spacing, layout, component, card, badge, or table
change is planned. The repair changes only the guarded fixture regression and the trusted browser
proof, satisfying `docs/working/FRONTEND_DESIGN_RULES.md`.
