# Review Packet: 2026-07-13_040511_repair

## Result
Repair ready for independent validation

## Slice
006Z10-portal-limit-interaction-and-boundary-proof

## Recommended Next Action
Run the declared trusted browser spec twice outside the sandbox, verify all four screenshots, then
perform full independent validation and commit only if every gate passes.

## Demonstrated Failure and Repair

Both prior trusted runs passed three scenarios, then timed out at `getByRole('checkbox').nth(8)`.
The declarations screen owns seven visible checkboxes; the eighth match was an unrelated hidden
shell switch (`switchInput`) whose label intercepted pointer events. The repaired helper names each
of the seven declaration controls exactly, preventing cross-shell selection and stale indexing.

## Traceability

- Slice requirement: execute the real MP05 submit/refetch/reload lifecycle and save
  `portal-limit-review-maximum.png`.
- Existing code: the routed browser scenario completes nominee, documents, declarations, review,
  submit, canonical returned-amount refetch, and reload.
- Repair proof: `e2e/portal-application-limit-authority.e2e.spec.ts` collects four scenarios; the
  exact-label declaration helper reaches only public, visible controls. The focused mounted MP05
  suite passes 7/7 and the complete frontend suite passes 207/207.
- Source fidelity: M04-FR-005 through M04-FR-007 remain server-authored. This repair introduces no
  client arithmetic, business rule, styling, API, or persistence change.

## Gate Summary

- Frontend build/typecheck/lint: pass.
- Frontend tests: 207 passed.
- Backend check/migration sync: pass.
- Backend tests/coverage: 500 passed, 12 expected skips, 93% coverage.
- Trusted browser: collection passes; two unsandboxed executions and screenshots pending the
  orchestrator contract.
