# Impact Analysis

Selected slice: `CR-012-epic-009-playwright-evidence-is-incomplete`
Mode: repair

## Demonstrated failure and affected browser module

- The authoritative failure is in the previous repair's
  `evidence/terminal-logs/trusted-browser-acceptance-1.log`: after the spec runs the guarded
  `seed_epic_009_e2e_fixture --make-ready` transition, Playwright times out because the visible
  `Initiate payment` button remains disabled.
- The same trusted log contains no `/api/v1/disbursement-workspaces/` GET after `--make-ready`.
  `sfpcl-lms/src/pages/disbursement/DisbursementHub.tsx` loads its workspace on component mount,
  while the current spec clicks the already-selected `SAP & Disbursement` navigation item after the
  out-of-browser fixture transition. The mounted screen therefore retains the earlier blocked row.
- The repair affects only
  `sfpcl-lms/e2e/epic-009-staff-disbursement-closure.e2e.spec.ts`: reload the authenticated app after
  the guarded fixture transition, reopen the screen, and assert the real refreshed action.

## Backend models, endpoints, and services

- Grep evidence identifies the guarded transition in
  `sfpcl_credit/identity/management/commands/seed_epic_009_e2e_fixture.py` and its endpoint regression
  in `sfpcl_credit/tests/test_seed_e2e_users.py`. The regression asserts that `--make-ready` makes
  readiness true and exposes `initiate_disbursement` through the real workspace endpoint.
- No backend model, endpoint, serializer, service, permission, fixture behavior, or API contract is
  changed. The preserved candidate continues to exercise real `/api/v1/auth/`,
  `/api/v1/loan-accounts/`, and `/api/v1/disbursement-workspaces/` boundaries.
- No additional backend regression is warranted for a browser-refresh defect. The existing seed/API
  regression remains the affected backend-module test and independent validation reruns the full
  configured backend gate.

## Frontend screens, routes, and blast radius

- The exercised production surfaces remain Loan Account list/summary, SAP & Disbursement, Payment
  Authorisation, notifications, and the genuine Django safe-error state. No production component,
  service, route, or navigation behavior changes.
- The direct blast radius is the CR-012 trusted browser spec. Reloading preserves the real staff
  session through the application-owned session mechanism and forces the existing component mount
  to fetch current owner evidence.
- Other Playwright specs, including the retained 009I2 MP14 contract, and all production consumers
  of the workspace API are unchanged.

## Regression tests and checks

- Browser module: rerun the exact declared spec. It must progress beyond Payment Initiation, capture
  all nine declared PNGs, and emit nine pairwise-distinct SHA-256 hashes.
- Backend module: retain and run the focused Epic 009 seed regression proving the real endpoint
  exposes the initiation action after `--make-ready`.
- Static harness: collect the exact Playwright spec and verify it contains no owned-route fulfilment
  or browser-storage authentication injection.
- Frontend gates: run the impacted frontend tests, typecheck, lint, and build as appropriate; full
  independent validation remains authoritative.

## Frontend design compliance

No production UI code, styling, colours, typography, spacing, layout, components, cards, badges, or
tables change. The repair only refreshes the trusted browser's real server-backed state, so
`FRONTEND_DESIGN_RULES.md` remains fully satisfied.
