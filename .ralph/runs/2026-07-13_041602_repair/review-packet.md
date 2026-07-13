# Review Packet: 2026-07-13_041602_repair

## Result
Repair ready for independent validation

## Slice
006Z10-portal-limit-interaction-and-boundary-proof

## Recommended Next Action
Run the declared trusted browser spec twice outside the sandbox, verify all four screenshots, then
perform full independent validation and commit only if every gate passes.

## Demonstrated Failure and Repair

Both trusted runs completed the first three scenarios and the fourth scenario's submit, canonical
refetch, and reload. They then timed out on the expected public provenance text. The component
received `calculated_as_of_date` and `calculation_rule_version` but rendered neither. A focused
mounted regression failed on that exact absence; the repair displays both fields beneath the
existing server amount cards.

## Traceability

- Source/slice: functional-spec M04-FR-005 through M04-FR-007 and 006Z10 requirement 4 require the
  retained stored-date projection to remain observable after reload.
- Code: `PortalApplicationLimitView` renders `As of <date> · Rule <version>` only from the public
  projection; it adds no client calculation or fallback.
- Proof: the mounted regression is red before and green after; the complete frontend suite passes
  207/207; the trusted spec still collects its four declared scenarios.

## Gate Summary

- Frontend build/typecheck/lint: pass.
- Frontend tests: 207 passed.
- Backend check/migration sync: pass.
- Backend tests/coverage: 500 passed, 12 expected skips, 93% coverage.
- Trusted browser: collection passes; two unsandboxed executions and screenshots pending the
  orchestrator contract.
