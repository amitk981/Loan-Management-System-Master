# Execution Plan

Selected slice: 006Z10-portal-limit-interaction-and-boundary-proof

Mode: repair

1. Reproduce the prior independent-browser failure with the focused trusted Playwright spec and
   preserve its exact checkbox interaction error as red evidence.
2. Minimise the failure to the declaration-control interaction and rank/test hypotheses without
   altering the preserved production or backend implementation.
3. Repair only the demonstrated browser-driver defect in the existing slice-specific E2E spec,
   using an observable label/control interaction that follows the current portal markup.
4. Run the focused spec twice when Chromium is available; otherwise run collection plus the
   closest deterministic non-browser checks and leave the trusted browser decision to the
   orchestrator as required by the slice capability.
5. Re-run configured frontend/backend gates in proportion to the narrow E2E-only change, save
   terminal evidence, verify protected paths/diff limits, and update the Ralph review artifacts,
   progress, handoff, state, and selected slice status without committing.

Permission check: `.ralph/runs/**`, `.ralph/progress.md`, `.ralph/state.json`, `docs/working/**`,
and `docs/slices/**` are allowed by `.ralph/permissions.json`. The existing uncommitted test repair
is under `sfpcl-lms/e2e/`; the owner-selected `localhost-e2e-server` slice and repair instruction
explicitly require that declared spec, so this plan limits any edit there to the demonstrated
trusted-browser failure. No protected, forbidden, source, production, schema, or dependency file
will be changed by this repair.
