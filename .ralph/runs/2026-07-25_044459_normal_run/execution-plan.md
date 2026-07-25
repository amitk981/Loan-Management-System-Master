# Execution Plan

Selected slice: 012DAA-reports-mis-frontend-wiring

## Scope

- Add a typed frontend report service for the six read-only 012A endpoints, using the shared
  authenticated pagination/error contract and only the source-defined query parameters.
- Add the section-8 `ordering` query seam missing from the six 012A selectors, with report-local
  public-field allowlists and deterministic tie-breakers; reject private/unknown fields.
- Replace mock-backed report-result reads and inline result fixtures in `ReportsMIS.tsx` while
  preserving the existing S69 layout, tabs, styling, and deferred export seam.
- Add the trusted `reports-exports-audit-explorer` browser spec and save its required
  `report-results.png` evidence from two passing runs.
- Do not implement export jobs/downloads, audit explorer behavior, new report definitions, or
  client-owned report calculations.

## Behavior-first sequence

1. RED: specify report request serialization, pagination, sorting, active-filter preservation,
   reconciliation fields, and 403 propagation through the public report service.
2. GREEN: implement the smallest typed report service that satisfies those request behaviors.
3. RED: specify S69 loading, seeded results/totals, filter/sort/page round-trips, empty/error/
   unauthorized states, permission loss, and deferred export behavior.
4. GREEN: wire `ReportsMIS.tsx` to the service using existing visual/state patterns and backend
   authority; keep page-local state limited to query/view concerns.
5. Add the declared Playwright route-backed acceptance for the report result screen and required
   screenshot, then run it twice against the localhost server.

## Verification and evidence

- Save each focused RED/GREEN command and output under `evidence/terminal-logs/`.
- Run the focused report service and component tests, then frontend typecheck, lint, unit tests,
  and build. Run focused 012A backend regressions only if needed for reconciliation evidence, using
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Record source-to-code-to-test traceability, report reconciliation/role-denial evidence, diff
  scope, risk assessment, and independent-validation readiness in the run packet.

## Guardrails checked

- Editable targets are limited to `sfpcl-lms/src/**`, `sfpcl-lms/e2e/**`, and this run's evidence.
- `docs/source/**`, workflow configuration, scripts, state/progress, selected-slice status, and
  other protected/mechanical files will not be changed.
- No dependency installation, git staging/commit/push, new styling, or unstated business rule.
