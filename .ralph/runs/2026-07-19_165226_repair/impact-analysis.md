# Impact Analysis

Selected slice: `CR-012-epic-009-playwright-evidence-is-incomplete`
Mode: repair

## Demonstrated failure

- The authoritative failure is retained in
  `.ralph/runs/2026-07-19_164219_repair/evidence/terminal-logs/trusted-browser-acceptance-1.log`.
  The declared real-Django flow posts CFC authorisation successfully (HTTP 200), refreshes the CFC
  workspace to an empty response, and then times out looking for `Action recorded successfully.`.
- `PaymentAuthorisationHub` renders its action alert only inside the selected-row branch. Once the
  approved item leaves the CFC actor's pending-only projection, the truthful visible UI is the empty
  queue state, not that nested alert. The repair must assert the real HTTP response and terminal
  visible queue state instead of expecting an element that cannot render without a selected row.

## Affected backend models, endpoints, and services

- No backend production change is planned. The real boundary exercised is
  `POST /api/v1/disbursements/{id}/authorise/`, followed by the existing paginated
  `GET /api/v1/disbursement-workspaces/` projection.
- Existing guarded fixture ownership remains in
  `sfpcl_credit/identity/management/commands/seed_epic_009_e2e_fixture.py`, with regression coverage
  in `sfpcl_credit/tests/test_seed_e2e_users.py`. The fixture grants the existing transfer-success
  capability and synthetic restricted evidence to the initiating Senior Finance actor because the
  real CFC projection is intentionally pending-only after authorisation.
- Backend blast radius is fixture-only: CFC authorisation, workspace scope, synthetic evidence
  ownership, and the existing Senior Finance transfer action. No production role catalogue,
  permission, endpoint, owner service, or model changes.

## Affected frontend screens, components, and routes

- The only repair target is
  `sfpcl-lms/e2e/epic-009-staff-disbursement-closure.e2e.spec.ts`.
- The exercised production consumer is
  `sfpcl-lms/src/pages/disbursement/PaymentAuthorisationHub.tsx`. It is inspected but not changed:
  its empty-queue branch truthfully reports `No payment authorisations in your scope` after the
  authorised row leaves CFC scope.
- `sfpcl-lms/src/services/disbursementApi.ts` remains unchanged. The browser spec will observe the
  genuine authorisation response directly while the application continues using the normal client.
- Other consumers, including the Senior Finance transfer view and the 009I2 MP14 browser contract,
  remain regression surfaces but receive no code change.

## Regression tests and validation

- Browser evidence module: the declared Playwright spec is the regression. It will await the exact
  real CFC authorisation POST, assert HTTP 200 and the approved response state, then assert the empty
  CFC queue is visible before advancing the guarded fixture. It then logs in as Senior Finance,
  performs the real transfer action, and asserts the successful/active Django response.
- Backend fixture module: regression assertions require the Senior Finance transfer grant and
  synthetic evidence ownership. The test was captured red before the guarded fixture was updated,
  then green afterwards.
- Run Playwright collection/static real-boundary checks, the focused frontend payment-authorisation
  test and existing guarded backend fixture test, then typecheck, lint, and build. Attempt the exact
  browser spec locally if Chromium launches; Ralph's two outside-sandbox runs remain authoritative.

## Frontend design compliance

No production UI, styling, colour, typography, spacing, layout, component, card, badge, or table
change is planned. This repair changes only the trusted browser assertion and follows the existing
empty-state pattern required by `docs/working/FRONTEND_DESIGN_RULES.md`.
