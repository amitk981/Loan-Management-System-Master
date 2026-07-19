# Impact Analysis

Selected slice: `CR-012-epic-009-playwright-evidence-is-incomplete`

## Affected backend pieces

- The isolated E2E seed boundary is extended with
  `sfpcl_credit/identity/management/commands/seed_epic_009_e2e_fixture.py`, alongside the existing
  `seed_e2e_users.py`. Grep evidence: the established command enforces both `SFPCL_DEBUG=true` and
  `SFPCL_ALLOW_E2E_SEED=true`, and `playwright.config.ts` invokes guarded seed commands before
  Django starts. The new command follows the same refusal/idempotency contract for deterministic
  Epic 009 staff actors and workflow state.
- Real owned endpoints are exercised, not changed: `config/urls.py` maps
  `/api/v1/loan-accounts/`, `/api/v1/loan-accounts/<uuid>/`, and
  `/api/v1/disbursement-workspaces/`; frontend services call those paths from
  `loanAccountsApi.ts` and `disbursementApi.ts`. Their models, services, serializers, permissions,
  money rules, and response shapes remain untouched.
- The fixture necessarily creates only synthetic rows already owned by applications, approvals,
  legal/security readiness, SAP workflow, loans, disbursements, communications, identity, audit,
  and workflow modules. It must use existing owner services/evidence shapes and remain unavailable
  outside the doubly guarded isolated database.

## Affected frontend and browser pieces

- `sfpcl-lms/e2e/epic-009-staff-disbursement-closure.e2e.spec.ts` is the primary defect surface.
  Grep found browser storage token injection and `page.route(...fulfill...)` stubs for `/auth/me/`,
  `/loan-accounts/`, and `/disbursement-workspaces/`. Those are replaced by real login-form and
  real-Django flows.
- `sfpcl-lms/playwright.config.ts` owns isolated database creation and seed command execution. It
  may need to invoke an Epic 009 seed/reset command before serving the backend.
- Existing production screens are consumed but not visually or behaviorally changed:
  `LoanAccount360.tsx`, `DisbursementHub.tsx`, and `PaymentAuthorisationHub.tsx`, reached through
  the existing `App.tsx` routes/sidebar. Existing API services and shared auth transport remain
  unchanged.
- The browser contract adds the missing `loan-account-list.png`; every one of the nine captures is
  preceded by an exact visible assertion and the spec writes/verifies a deterministic SHA-256
  manifest with nine unique hashes.

## Blast radius and other consumers

- `seed_e2e_users` is consumed by every Playwright spec through the shared web server, so the seed
  must remain idempotent and preserve the tracer, zero-permission, and Epic 006 fixtures exactly.
- Any new Epic 009 fixture helper is also consumed by the trusted Epic 009 spec and must not alter
  normal application startup, demo seed data, migrations, or production databases.
- Loan Account and disbursement-workspace endpoints are also consumed by the production staff
  screens, their component tests, member/notification navigation, and backend API/selector tests.
  Since this correction changes no endpoint or production UI code, those consumers should observe
  no behavior change.
- Playwright config is shared by all browser specs. The fresh isolated database and guarded seed
  sequence must continue to support existing tracer, Epic 006, MP14, and other trusted specs.

## Existing coverage and regressions to add

- Backend identity/seed module: `tests/test_seed_e2e_users.py` already covers guard refusal,
  idempotency, real login, permissions, and preservation of existing fixtures. Add failing-first
  tests proving Epic 009 actors/state are created, the seed remains idempotent, both guards remain
  mandatory, and real owned list/workspace endpoints expose the intended deterministic states to
  the intended actors.
- Backend Loan Account and workspace modules: existing `test_loan_account_reads_api.py`,
  `test_disbursement_workspace_api.py`, and Epic 009 selector equivalence/PostgreSQL tests cover
  production endpoint behavior. Add no duplicate production-policy tests; the new seed regression
  will call these public endpoints and assert the seeded contract.
- Frontend screens/services: existing `LoanAccount360.test.tsx`, `DisbursementHub.test.tsx`,
  `PaymentAuthorisationHub.test.tsx`, `loanAccountsApi` tests, and `disbursementApi` tests retain
  component/transport behavior. The changed Playwright spec is the regression for the browser
  module: real form login, no owned-route fulfilment, nine state assertions/screenshots, and
  pairwise hash uniqueness.
- Shared Playwright harness: run Playwright collection locally because Chromium may be unavailable;
  the orchestrator executes the exact trusted spec twice and owns authoritative screenshots.

## Frontend design compliance

No production component, styling, colour, typography, spacing, layout, card, badge, or table is
changed. The proof drives and captures the existing prototype-approved screens only, satisfying
`FRONTEND_DESIGN_RULES.md` without any design exception.
