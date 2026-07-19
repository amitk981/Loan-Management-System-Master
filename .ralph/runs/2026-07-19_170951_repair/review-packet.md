# Review Packet: 2026-07-19_170951_repair

## Result
Ready for independent validation

## Slice
CR-012-epic-009-playwright-evidence-is-incomplete

## Demonstrated Failure and Fix

The retained trusted run used real Django successfully but selected Credit Manager for a sanctioned
account. The canonical loan-account owner only admits Credit Managers after activation, so the first
row assertion failed before any screenshot. The repaired flow uses the assigned Senior Finance actor
for the sanctioned list/summary, then uses Credit Manager for the active summary after the real
transfer response. Finance returns for the genuine nondisclosing Django error.

## Scope Review

- Preserved the quarantined CR-012 implementation and changed only the demonstrated actor mismatch
  plus its focused fixture/read regression.
- No production API shape, model, selector, permission, business rule, money calculation, workflow,
  visual style, route, or component changed.
- The browser still authenticates Credit Manager, Senior Finance, and CFC through the real login
  form; it does not inject tokens or fulfil owned APIs through Playwright routing.
- Every declared capture retains its immediately preceding visible assertion. Stale screenshot and
  manifest cleanup, exactly nine basenames, SHA-256 generation, and within-run hash uniqueness remain.
- Safe error evidence still comes from navigation to an inaccessible UUID and a genuine Django 404.

## Traceability

The slice says the nine Epic 009 states must use real Django, state-specific visible assertions,
three real staff actors, and distinct SHA-256 evidence. The spec does exactly that; the guarded seed
and real-endpoint test verify the sanctioned actor boundary, Playwright collection verifies the
declared contract is runnable, and Ralph's twice-run trusted browser gate will verify all nine PNGs
and both manifests outside the sandbox.

## Validation Evidence

- Guarded seed suite: 11/11 passed, including real Finance/Credit loan-account scope assertions.
- Impacted frontend suite: 13/13 passed across LoanAccount360, DisbursementHub, and
  PaymentAuthorisationHub.
- Playwright collection: one exact declared Chromium test collected.
- Static owned-API stub scan: passed; no `page.route` or `route.fulfill`.
- Typecheck, lint, build, Django check, migration sync, and diff hygiene: passed.
- Complete backend/coverage and twice-run trusted browser acceptance: deliberately delegated to the
  orchestrator per the run contract.

## Review Findings

- Correct root cause: evidence actor selection contradicted the existing canonical status scope.
- Regression seam: exact guarded fixture plus real API; no production seam was weakened to make the
  proof pass.
- No debug instrumentation, fabricated screenshot, new dependency, migration, or protected-path edit.

## Recommended Next Action
Run full independent validation, including the declared browser spec twice with clean evidence
directories. Commit only if both runs retain all nine structurally valid, content-distinct PNGs and
their deterministic manifests.
