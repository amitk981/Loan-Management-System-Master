# Execution Plan — 005E2 Completeness Workbench Real-Data Corrective

## Scope and constraints

- Change only the Epic 005 completeness workbench frontend and its existing application-intake API seam.
- Preserve the approved screen structure and styling; replace only data, states, and action authority.
- Do not change backend business rules. The existing 005D/005E/005F/005F2/005H endpoints remain authoritative.
- Remove every `mockData` read, seeded deficiency, manual checklist decision, and client reference calculation from `CompletenessWorkbench.tsx`.

## Behavior-first implementation sequence

1. Add an API-client test for completeness read/pass, return-with-deficiencies, deficiency resolution, and rejection-note creation. Run it alone and save the expected RED output.
2. Implement only those typed API-client functions and rerun the client test to GREEN.
3. Add workbench component tests proving API queue rows/checklist/history render, backend `available_actions` controls actions, and pass/return/reject requests use exact bodies and re-render backend state. Save RED output before changing the page.
4. Replace the mock-backed page with an API-backed container and a testable view composed from the existing card, badge, alert, table/queue, and modal patterns. Surface loading, empty, error/unauthorized, validation, and stale-conflict states.
5. Rerun focused tests after each behavior, then run the full frontend lint, typecheck, test, and build gates.
6. Capture self-contained visual evidence for queue/detail/pass/deficiency/returned states using the existing browser/e2e harness if available; otherwise save deterministic rendered evidence in the run folder and document the limitation.
7. Update API contract notes only if the UI exposes an interim permission rule; update prototype inventory/gap ledgers, slice status, Ralph state/progress/handoff, and required run artifacts.
8. Sharpen the next one or two Not Started slices using only source material already opened during this run, then perform protected-path/diff-limit checks.

## Permissions and risk

- Allowed edit paths confirmed in `.ralph/permissions.json`: `sfpcl-lms/src/**`, `docs/working/**`, `docs/slices/**`, `.ralph/state.json`, `.ralph/progress.md`, and `.ralph/runs/**`.
- Medium risk: staff workflow actions mutate application state, but this slice delegates all decisions, validation, permissions, audit events, and reference issuance to existing backend endpoints.
