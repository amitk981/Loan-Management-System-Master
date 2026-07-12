# Review Packet: 2026-07-13_024405_repair

## Result
Ready for independent validation

## Slice
006Z8-portal-limit-provenance-module-and-interaction-closure

## Recommended Next Action
Run the full Ralph validator, including both trusted browser runs and four screenshot checks. If it
passes, commit the quarantined slice and proceed to the due architecture review.

## Demonstrated Failure and Repair

Both prior trusted runs recorded two identical initial projection GETs instead of one. The app root
uses React StrictMode, which replays mount effects in development. MP05 now records that its initial
projection has been requested before starting the async read, preventing the replay while leaving
explicit post-submit canonical refetches untouched.

## Traceability

- Slice requirement 4 says the controlled requested amount drives the projection and canonical
  refetch behavior. The initial call remains `requested_amount=500000`; successful submit still
  calls `loadLimitProjection` explicitly.
- Slice requirement 5 requires exact request method/URL/body in the routed container. The focused
  StrictMode test asserts one GET to the exact borrower-scoped URL; the Playwright contract retains
  the same exact assertion.
- Slice requirement 6 forbids client authority calculation and visual changes. Neither rendering
  nor money logic changed, and the existing static regressions remain green.

## Evidence

- Red: `evidence/terminal-logs/strict-mode-projection-red.log` — two projection calls observed.
- Green: `evidence/terminal-logs/strict-mode-projection-green.log` — five focused tests pass.
- Frontend: typecheck, lint, 205 tests, and build pass in `evidence/terminal-logs/`.
- Backend: Django check, migration sync, 494 tests (12 expected skips), and 93% coverage pass.
- Browser: four tests collect. Local launch is sandbox-denied before execution; no screenshots were
  fabricated, and the independent validator owns both trusted runs.
