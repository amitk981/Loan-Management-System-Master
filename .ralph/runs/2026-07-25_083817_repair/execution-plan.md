# Execution Plan

Selected slice: 012G-critical-e2e-uat-smoke-scenarios

Mode: same-worktree repair

## Authoritative failure

The trusted browser launched successfully and reached the public subsidiary-repayment replay.
The replay returned an explicit idempotency wrapper containing `idempotency_replayed: true` and
`original_response`, while the E2E assertion incorrectly compared the entire wrapper to the
original response body.

## Bounded plan

1. Preserve the current candidate and inspect the public repayment idempotency contract plus
   existing regression assertions for the replay response shape.
2. Confirm edit permissions for the current run evidence and the selected slice's E2E spec.
3. Add a focused regression assertion at the existing E2E seam, capture the red-capable mismatch,
   and minimally align the assertion with the confirmed public contract.
4. Rerun the exact trusted-browser command named by the validator until the declared spec passes
   and both declared screenshots are produced; save terminal output and screenshot hashes.
5. Run the focused frontend test for the seed/UAT support plus frontend typecheck, lint, and build.
   Do not run the complete backend suite or coverage; independent validation owns that lane.
6. Inspect targeted diff/stat and protected paths, then complete risk assessment, review packet,
   and concise repair evidence. Set the review result exactly to the required validation-ready
   phrase only after focused gates are green.

## Scope guard

No business rules, production APIs, models, permissions, UI styling, source documents, protected
workflow files, mechanical state/progress/status facts, or unrelated slices will be changed.

## Completion note

Steps 1-3 and 5-6 are complete. The exact browser command was rerun twice, but both local attempts
ended before page creation because Chrome closed during launch. This is retained as infrastructure
evidence and does not override the prior orchestrator-owned post-launch assertion. Per the trusted
browser contract, independent validation owns the authoritative rerun and screenshot decision.
