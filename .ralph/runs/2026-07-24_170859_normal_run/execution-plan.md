# Execution Plan

Selected slice: 012EB-task-inbox-frontend-wiring

## Boundary

- Wire only S03 Task Inbox and its declared Dashboard parity/inventory contracts to the existing
  012EA APIs.
- Preserve the existing Task Inbox visual composition; add no styling system or backend behavior.
- Do not expose task export because 012EA defines no task-export endpoint; record that decision in
  the working API contract.
- Do not edit protected/source/orchestrator-owned files.

## Test-first implementation

1. Add a focused Task Inbox public-interface test for authenticated list loading, strict
   pagination, and API query parameters; run it RED and save output.
2. Add the minimal task API client and screen container/view wiring to make that behavior GREEN.
3. Add one behavior at a time for loading/empty/error/unauthorized states, S03 columns, linked
   navigation, permitted actions, backend denial, and dashboard task parity; save focused RED/GREEN
   output.
4. Add the trusted Playwright contract for populated, filtered, action, and unauthorized states
   using deterministic intercepted API responses, then run the declared browser contract twice and
   save its four screenshots when Chromium is available.
5. Update the API contract export decision and the two prototype tracking documents; prove Task
   Inbox has no mock/fixture read and audit remaining staff mock imports against the declared
   ownership ledger without expanding this slice into other screens.

## Validation and evidence

- Run focused Task Inbox and Dashboard Vitest files during development.
- Run frontend typecheck, lint, build, and impacted tests; do not run backend complete coverage.
- Save terminal logs, browser artifacts/screenshots, mock-removal search output, risk assessment,
  and a spec/standards self-review in this run directory.
- Finish with `review-packet.md` Result exactly `Ready for independent validation`.
