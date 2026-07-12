# Execution Plan

Selected slice: `006Y9-member-form-real-session-closure`

1. Reproduce the demonstrated trusted-browser failure with the exact declared Playwright scenario
   and preserve its output as the failing-first repair signal.
2. Inspect the routed member create/refetch behavior and existing E2E navigation patterns, rank
   falsifiable causes, and change only the browser scenario assertion/navigation that conflicts
   with the real production route. Preserve all production code and prior slice work unless the
   reproduction proves a production defect.
3. Re-run the focused scenario to green twice, verify all four declared screenshots are non-empty,
   then run Playwright collection and the configured frontend/backend gates with the mandated
   backend interpreter.
4. Save terminal evidence, changed-files, risk assessment, review packet, and final summary; update
   Ralph progress/state/handoff and the selected slice only as required by the repair result.
