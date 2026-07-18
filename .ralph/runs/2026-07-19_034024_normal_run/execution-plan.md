# Execution Plan

Selected slice: `009K-disbursement-and-cfc-frontend-wiring`

## Boundary and permissions

- Implement only the staff disbursement and CFC authorisation frontend wiring owned by 009K.
- Product edits are limited to permitted `sfpcl-lms/src/**` paths and, only if contract documentation is genuinely changed, permitted `docs/working/**` paths.
- Evidence edits are limited to `.ralph/runs/2026-07-19_034024_normal_run/**`.
- Do not edit protected paths, `docs/source/**`, Ralph-owned state/progress/status bookkeeping, or unrelated future slices.
- Inspection found no safe staff queue spanning the existing mutation APIs, so the slice adds a
  read-only backend-for-frontend projection. Existing domain modules remain authoritative for
  readiness, money, permissions, idempotency, UTR uniqueness, and advice state; the projection
  composes those decisions and never duplicates their business rules.

## Implementation sequence

1. Read the bounded Epic 009 digest sections and cited source excerpts needed for screens S36-S41, then inventory existing frontend routes, API-client conventions, role seams, and the two owned mock screens.
2. Add focused frontend tests first for the observable 009K contracts: backend-driven loading/error/unauthorised/empty/blocked/success states, named readiness blockers, disabled initiation, stable idempotency replay handling, CFC-only actions, rejection reason, and duplicate-UTR error display.
3. Implement typed disbursement API adapters/hooks using the shared transport and Money contract. Recompose the two existing screens without adding styling or visual patterns, remove all owned mock imports/inline business fixtures, and preserve server authority for state and actions.
4. Run focused tests iteratively, then frontend typecheck, lint, all frontend tests, and build. Do not run the complete backend suite; run backend checks only if inspection shows the slice unexpectedly requires backend changes.
5. Inspect targeted diffs and mock-removal searches, perform the required review, and save self-contained terminal logs, visual/browser evidence where locally possible under the declared acceptance constraints, risk assessment, review packet, and final summary.

## Acceptance trace

- S37: SAP request/confirmation state is fetched and completion calls the existing API. S36 create
  and send require a Credit Manager candidate/assignee selection contract that the bounded backend
  does not expose; this remains an explicit acceptance gap rather than an invented raw-ID form.
- S38: readiness result and named blockers are rendered; initiation remains unavailable while blocked.
- S39: initiation submits Money payload with a stable `Idempotency-Key`; replay is represented without a duplicate client outcome.
- S40: CFC queue and authorise/reject actions are role-gated in the UI while backend 403 responses remain visible.
- S41: UTR capture/duplicate validation, transfer success, and advice delivery status come from backend responses.
- Both owned screens contain no `mockData` imports or inline business fixtures and cover loading, empty, error, unauthorised, blocked, validation, and success states using existing patterns.
