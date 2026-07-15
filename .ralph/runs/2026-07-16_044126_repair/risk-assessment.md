# Risk Assessment

Risk level: High (selected-slice declaration); Medium incremental repair risk.

- Demonstrated failure: the real external browser clicked `Record stamp` on a completed Term Sheet;
  Django correctly returned `409`, while the spec waited for a success state and produced no final
  screenshots.
- Root cause: the workspace action projection checked actor authority but ignored the checklist
  item's terminal completion state before advertising signature/stamp/notary mutations.
- Repair scope: completed or stale-terminal items no longer receive legal-evidence mutations;
  pending items retain the same owner-authorised actions. The browser now checks the impossible
  button is absent, gets `200` for the exact replay-safe completion action, then proves a changed
  replay remains `409` and the restricted content request remains `404`.
- No schema, dependency, permission catalogue, styling, protected file, or source document changed.
- Controls: failing-first backend projection regression, pending/complete parity tests, full local
  frontend/backend gates, coverage floor, browser collection, protected-path inspection, and the
  1,998/2,000 diff limit.
- Residual risk: Chromium cannot launch in the coding sandbox. Independent Ralph validation must
  run the spec twice and verify all four non-empty screenshots before commit/merge.
