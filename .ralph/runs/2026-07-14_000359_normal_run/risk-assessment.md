# Risk Assessment

Risk level: Medium

- Selected slice: 007J-registers-and-approval-matrix-frontend-wiring
- Mode: normal_run
- Standing approval: active; no revoked entry applies.

## Security and integrity assessment

- S23 and S25 consume their independent, already actor-scoped list endpoints. Every response
  replaces both rows and server pagination; no case/detail call repairs a row or expands scope.
- Canonical register and matrix permissions map to resource-scoped navigation capabilities, not
  the legacy whole-hub permissions. Backend sessions holding only these capabilities see only the
  owned panels, and permission loss removes prior actor data before any prototype fixture can show.
- S23 document and case identifiers remain text metadata. No case action, evidence selection, or
  download affordance is introduced.
- Matrix mutation remains server-governed: the UI submits a complete successor PATCH and reports
  the returned pending maker-checker proposal. It neither activates nor overwrites the active rule.

## Regression and operational risk

- The wide frozen-fact tables and successor form reuse existing table, Tabs, alert, modal, field,
  and button patterns. A-091 records why focused components were necessary and the design seams used.
- Tests cover canonical FY application, independent filters/pages, all nested frozen references,
  resource-scoped navigation, stale-data removal, hidden matrix editing, direct PATCH 403, and
  pending-proposal submission.
- Export is intentionally non-operational until 012B/012C. The permitted button shows an explicit
  deferred notice and performs no network request; API_CONTRACTS records that interim behavior.

## Gate outcome

- Frontend: production build, typecheck, lint, and 245 tests pass.
- Backend: check and migration sync pass; 680 tests pass with 19 expected skips; coverage is 93%.
- Visual: the sandbox denied the localhost Vite listener with `EPERM`; the genuine attempt log is
  retained and no screenshot was fabricated.
- Diff: no migrations or dependencies; protected/source paths unchanged; `git diff --check` clean.
- Manual review required: orchestrator independent validation before commit/merge/push.
