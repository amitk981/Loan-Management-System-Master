# Review Packet: 2026-07-19_163229_repair

## Result
Ready for independent validation

## Slice
CR-012-epic-009-playwright-evidence-is-incomplete

## Demonstrated Failure and Fix

- Independent validation proved the real initiation POST and refreshed workspace GET both returned
  HTTP 200, then failed waiting for `Payment initiation recorded successfully.`
- Production `DisbursementHub` refreshes rows before setting that message and nests the banner in
  the current action card. A successful initiation consumes that action, so the assertion targeted
  an element removed by the successful transition.
- The spec now waits for the genuine Django mutation response, asserts its exact initiated/pending
  state, then asserts the consumed action is hidden and the refreshed Pending state is visible.

## Scope Review

- Repair delta: `sfpcl-lms/e2e/epic-009-staff-disbursement-closure.e2e.spec.ts` only.
- Preserved candidate: guarded idempotent Epic 009 fixture, real staff login, real owned APIs, nine
  state-specific captures, safe Django error, stale-file cleanup, and unique SHA-256 manifest.
- No production component, backend behavior, API shape, permission, styling, money, or workflow
  contract changed. No protected path changed, and diff hygiene is clean.
- No browser interception/fulfilment of owned routes or auth-storage injection is present.

## Validation Evidence

- Focused guarded backend seed/API regression: PASS (1 test).
- Impacted disbursement frontend regressions: PASS (8 tests across 2 files).
- Exact Playwright collection: PASS (1 declared Chromium test).
- Typecheck, lint, and production build: PASS.
- Static real-boundary/auth-injection scan and `git diff --check`: PASS.
- Local browser attempt: Chrome infrastructure closed at launch before the test body; no screenshot
  evidence was fabricated. The twice-run independent trusted-browser contract remains mandatory.

## Traceability

The CR and slices 009J/009K say Epic 009 must retain nine asserted, content-distinct screenshots
through authenticated real Django boundaries. The preserved spec logs in through the staff form,
uses real Loan Account and workspace APIs, asserts each captured state, deletes stale evidence, and
rejects duplicate hashes. This repair proves the initiation transition with the real response's
server-owned statuses and the refreshed visible state, avoiding dependence on an impossible
transient banner. The exact Playwright spec and focused seed regression verify this contract; the
orchestrator's two trusted runs must provide the final PNG and manifest proof.

## Recommended Next Action
Run complete independent validation, including both trusted browser repetitions with fresh
nine-image manifests. Commit only if every configured gate passes.
