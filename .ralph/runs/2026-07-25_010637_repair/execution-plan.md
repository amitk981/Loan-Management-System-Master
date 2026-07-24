# Execution Plan

Selected slice: 011PC-closure-frontend-wiring

## Repair Boundary

Repair only the demonstrated `localhost-e2e-server` validation domain for the preserved 011PC
candidate. The prior validator failed before page creation because Google Chrome exited during
Playwright launch, leaving both required trusted-browser screenshot runs incomplete.

## Plan

1. Preserve the existing product candidate and inspect the exact Playwright configuration,
   slice-owned spec, screenshot contract, and validator invocation.
2. Reproduce the failure with the smallest agent-runnable browser launch probe, then run the exact
   declared S58-S61 Playwright scenario.
3. Rank and test browser-domain hypotheses one at a time. Change only the E2E/config/spec surface if
   the failure is candidate-controlled; do not alter unrelated product behavior to compensate for
   runtime infrastructure.
4. Run the exact declared spec twice, retaining distinct passing logs and the required
   `closure-readiness-blockers.png` output/manifest for both runs.
5. Re-run the impacted frontend test, typecheck, lint, and build only if a candidate file changes.
   Save all repair evidence under this run directory.
6. Complete the risk assessment, review packet, and final summary. Set the review result exactly to
   `Ready for independent validation`.

## Permissions Check

- Allowed repair writes: `sfpcl-lms/e2e/**`, other `sfpcl-lms/**` paths if directly required, and
  `.ralph/runs/2026-07-25_010637_repair/**`.
- Protected/forbidden paths remain read-only, including `scripts/**`, `.ralph/config.yaml`,
  `.ralph/permissions.json`, `docs/source/**`, and all policy/guardrail files.
- No git metadata, dependency installation, backend business logic, queue state, slice status, or
  mechanical handoff changes are authorized.
