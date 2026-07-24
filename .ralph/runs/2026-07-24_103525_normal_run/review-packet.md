# Review Packet: 2026-07-24_103525_normal_run

## Result
Ready for independent validation

## Slice
012E-operational-dashboard-hardening

## Implementation

- Added the general and three dedicated operational dashboard routes with authenticated,
  primary-role-derived contexts and mismatch denial.
- Added stable Credit, CFO/Director, Compliance/CS/Auditor, Treasury/CFC, Accounts, and safe
  Management catalogues. Cards require their owning permission and use canonical actor/object
  scopes; tasks deliberately remain empty for 012EA/012EB.
- Wired the existing Dashboard patterns to the real API with loading, empty, forbidden, error,
  refresh, strict count validation, and exact scoped-link navigation. Application list consumes the
  completeness card's `status/current_stage` filters.
- Added the exact trusted-browser spec and four required screenshot names.

## Source Traceability

- `docs/source/api-contracts.md` §43-44: all four routes, stable summary shape, and `tasks: []`.
- `docs/source/information-architecture.md` §9.1: operational role/card families.
- `docs/source/technical-architecture.md` §21.1-21.2 and §24: server-side authorisation,
  read-model/query constraints, and no client role override.
- `docs/source/test-plan.md` §18.2 and §24.1-24.2: permission/isolation coverage and PERF-002
  query instrumentation without a flaky unit wall-clock assertion.
- `docs/source/screen-spec.md` §12: reuse of the existing KPI/task and state patterns.

## Independent Review

- Standards review findings for fake-zero permission handling, management fallback safety,
  role-family batching, direct global counts, and styling were repaired.
- Spec review findings for actor-aware counts, management safety, application reverse-consumer
  filtering, and role-family scoped URL preservation were repaired.
- The remaining broad target-worklist behavior is independently permission-checked by its owning
  module; trusted validation should exercise the full browser route matrix.

## Validation Evidence

- Backend focused: 17 tests passed — `evidence/terminal-logs/backend-focused-final.log`.
- Frontend focused: 26 tests passed — `evidence/terminal-logs/frontend-focused-final.log`.
- Django check and migration drift: passed — `backend-check-final.log`,
  `backend-migrations-final.log`.
- Frontend typecheck, lint, and build: passed — corresponding `*-final.log` files. Build reports only
  the pre-existing Vite chunk-size advisory.
- RED/GREEN evidence includes completeness, dedicated-route, query-budget, refresh/navigation,
  invalid-count, and canonical-scope budget logs.
- Reconciliation and query evidence: `evidence/role-card-reconciliation.md` and
  `evidence/dashboard-performance.md`.
- Browser attempt: `evidence/terminal-logs/browser-operational-dashboard.log`. Chromium aborted at
  launch, so the four trusted screenshots are intentionally absent and must be produced by trusted
  validation.

## Recommended Next Action
Run independent Ralph validation, including its authoritative backend lane and trusted browser
acceptance. Do not promote if the four required screenshots are not produced there.
