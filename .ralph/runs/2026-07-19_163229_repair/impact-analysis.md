# Impact Analysis

Selected slice: `CR-012-epic-009-playwright-evidence-is-incomplete`
Mode: repair

## Demonstrated failure and affected browser module

- The authoritative failure is
  `.ralph/runs/2026-07-19_162514_repair/evidence/terminal-logs/trusted-browser-acceptance-1.log`:
  the real `initiate_disbursement` POST returned HTTP 200 and the subsequent real workspace GET
  returned HTTP 200, but Playwright timed out waiting for
  `Payment initiation recorded successfully.`
- `sfpcl-lms/src/pages/disbursement/DisbursementHub.tsx` refreshes workspace rows before storing the
  success message and renders that message only inside the current action card. A successful
  initiation consumes the initiation action, so the card can disappear before the message is
  visible. This is an assertion mismatch in the evidence spec, not a failed mutation.
- The repair affects only
  `sfpcl-lms/e2e/epic-009-staff-disbursement-closure.e2e.spec.ts`: wait for and validate the genuine
  Django mutation response, then assert a visible post-initiation state before changing actors.

## Backend models, endpoints, and services

- Grep evidence identifies the guarded fixture command in
  `sfpcl_credit/identity/management/commands/seed_epic_009_e2e_fixture.py` and its endpoint regression
  in `sfpcl_credit/tests/test_seed_e2e_users.py`.
- The exercised owned boundaries are `/api/v1/auth/**`, `/api/v1/loan-accounts/**`, and
  `/api/v1/disbursement-workspaces/**`, including the initiation action URL supplied by Django.
- No backend model, endpoint, serializer, service, permission, fixture transition, workflow rule,
  or API contract changes. The existing seed/API regression remains the backend-module regression;
  the repair adds no backend behavior that warrants another backend test.

## Frontend screens, routes, and blast radius

- The exercised production surfaces remain Loan Accounts, SAP & Disbursement, Payment
  Authorisation, notifications, and the genuine Django safe-error screen.
- No production component, service, router, or navigation behavior changes. The direct blast radius
  is the CR-012 Playwright spec and its sequencing after the initiation click.
- Other browser specs, including the retained 009I2 MP14 evidence contract, and all production
  consumers of the workspace API remain unchanged.

## Regression tests and checks

- Browser evidence module: the declared Epic 009 spec is the regression test. It must validate the
  real initiation response, observe a visible post-initiation state, complete all later workflow
  states, write nine PNGs, and prove nine distinct SHA-256 hashes.
- Backend fixture module: retain and run the focused Epic 009 seed regression proving `--make-ready`
  exposes the initiation action through the real workspace endpoint.
- Static/collection feedback: collect the exact Playwright spec and run the frontend-focused tests,
  typecheck, lint, and build. The orchestrator's two unsandboxed trusted-browser executions remain
  the authoritative screenshot gate.

## Frontend design compliance

No production UI code, styling, colours, typography, spacing, layout, component, card, badge, or
table changes. The repair changes only how the trusted browser proves a real server-backed mutation,
so `docs/working/FRONTEND_DESIGN_RULES.md` remains satisfied.
