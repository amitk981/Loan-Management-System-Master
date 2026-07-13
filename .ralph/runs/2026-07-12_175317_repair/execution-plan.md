# Execution Plan

1. Read the prior trusted-browser logs and the Epic 004 digest, then identify the exact first failing assertion in the declared Playwright spec.
2. Run the narrow declared Playwright command (or collection when Chromium is sandbox-blocked) to establish a deterministic feedback loop for that assertion.
3. Rank and test focused hypotheses against the preserved e2e spec and production member profile without changing unrelated behavior.
4. Apply only the demonstrated browser-contract repair, then rerun the narrow feedback loop and relevant frontend tests.
5. Run configured frontend/backend quality gates, save evidence and review artifacts, and update Ralph state/progress/handoff/slice status only to reflect verified results.

No production behavior, backend business rule, visual system, or protected file is in scope unless the demonstrated failure proves it necessary.
