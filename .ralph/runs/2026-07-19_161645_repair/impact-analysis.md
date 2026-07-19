# Impact Analysis

Selected slice: `CR-012-epic-009-playwright-evidence-is-incomplete`
Mode: repair

## Demonstrated failure and affected browser module

- The authoritative failure is in
  `.ralph/runs/2026-07-19_154507_normal_run/evidence/terminal-logs/trusted-browser-acceptance-1.log`:
  `getByText('Sanctioned', { exact: true })` resolves both the sanctioned status badge and the
  sanctioned KPI label on Loan Account 360, so Playwright strict mode stops before eight remaining
  screenshots are produced.
- The repair affects only
  `sfpcl-lms/e2e/epic-009-staff-disbursement-closure.e2e.spec.ts`. Its sanctioned-summary assertion
  will be scoped to the existing status badge semantics. The same spec remains the regression test
  for all nine real-Django browser states and pairwise-distinct screenshot hashes.

## Backend models, endpoints, and services

- No backend model, endpoint, service, serializer, permission, fixture behavior, or API contract is
  changed by this repair.
- The preserved candidate implementation uses the guarded
  `seed_epic_009_e2e_fixture` command and real `/api/v1/auth/`, `/api/v1/loan-accounts/`, and
  `/api/v1/disbursement-workspaces/` endpoints. The trusted log proves real Django returned the login,
  current-user, account-list, and account-detail responses before the assertion failed.
- Existing backend regressions remain in `sfpcl_credit/tests/test_seed_e2e_users.py`; no additional
  backend regression is warranted for a locator-only defect because backend behavior is unchanged.

## Frontend screens, routes, and blast radius

- The exercised production screens are the existing Loan Account list/summary, SAP & Disbursement,
  Payment Authorisation, notifications, and safe-error states. No production component or route is
  edited.
- The only direct consumer is the CR-012 trusted browser contract. The shared Playwright config,
  other E2E specs (including 009I2 MP14), API services, and production pages remain unchanged.
- A semantically scoped status assertion preserves the strength of the state proof while avoiding
  accidental coupling to the separate KPI label. Every subsequent state remains covered by its
  existing assertion and screenshot.

## Regression tests and checks

- Browser module: rerun the exact spec
  `e2e/epic-009-staff-disbursement-closure.e2e.spec.ts`; it must complete all nine captures and write
  a manifest with nine different SHA-256 values.
- Harness/static boundary: collect the exact Playwright spec and inspect it for forbidden
  `page.route()` fulfilment or browser-storage authentication injection.
- Backend module: retain the already-green focused seed/API regressions from the normal run; the
  independent validator will rerun the complete configured suite.

## Frontend design compliance

No production UI code, styling, colours, typography, spacing, layout, components, cards, badges, or
tables change. The repair only narrows a test locator against an existing approved badge pattern, so
`FRONTEND_DESIGN_RULES.md` remains fully satisfied.
