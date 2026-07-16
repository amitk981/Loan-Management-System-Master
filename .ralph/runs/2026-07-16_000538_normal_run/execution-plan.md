# Execution Plan

Selected slice: `008M-documentation-hub-frontend-wiring`

1. Inspect the existing staff documentation prototype, current authenticated frontend API clients,
   the 008K5/L4 checklist/security/current-document projections, and the closest existing UI/test
   patterns. Confirm the exact server DTO allowlist and mutation/download routes before defining
   client types.
2. Add focused frontend tests first for the staff documentation client and rendered hub: loading,
   empty, forbidden, blocker, restricted, terminal-status-plus-download, current-role approval,
   conflict-without-optimism, refetch-on-success, and owned mock-removal behavior. Capture the
   intentional failing output in `evidence/terminal-logs/`.
3. Implement the smallest backend projection extension only if the existing public staff boundary
   cannot provide one locked S26-S35 snapshot. Any backend/business-logic change will start with a
   focused failing backend test and use the mandated Ralph virtualenv interpreter.
4. Implement a typed staff documentation API client and wire `DocumentationHub`,
   `DocumentChecklist`, `DocumentPackModal`, and `AuditTimeline` to backend-owned state and
   `available_actions`. Reuse existing visual structures; remove all owned `mockData` imports and
   inline business fixtures/calculations. Use the central signed-capability content flow with
   delayed object-URL revocation, and never retain or display forbidden evidence fields.
5. Run focused tests/typecheck throughout, then frontend lint, typecheck, full Vitest suite, and
   build. Run Django check, migration drift, and full backend coverage if backend code changes (and
   the normal Ralph-required backend gates before completion regardless). Save green logs and
   reviewable visual evidence; if Chromium is sandbox-blocked, record honest collection/non-browser
   evidence without fabricating screenshots.
6. Update API/visual inventory/gap documentation only where the delivered contract changes it.
   Complete `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, `final-summary.md`, state,
   progress, handoff, and the selected slice status. Sharpen the next one or two Not Started slices
   using already-opened source/digest facts, then perform the required independent review pass.
