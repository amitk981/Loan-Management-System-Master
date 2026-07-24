# Execution Plan

Selected slice: 011PC-closure-frontend-wiring

Mode: same-worktree repair

## Failure Boundary

Repair only the trusted-browser acceptance failure reported by
`.ralph/runs/2026-07-25_014323_repair/failure-summary.md`. Preserve the current product candidate.
The named validator's first Playwright run reached the S58-S61 closure screen but failed because
`getByText('LN-BROWSER-CLOSURE-001')` matched both the account-reference row and the checklist
heading. The second run and both screenshot manifests were then correctly deferred/missing.

## Permission Check

- Allowed run evidence: `.ralph/runs/2026-07-25_015201_repair/**`.
- Candidate repair target: `sfpcl-lms/e2e/default-closure-compliance-staff.e2e.spec.ts`, a
  slice-declared trusted-browser test inside the active worktree.
- No protected, forbidden, source, orchestrator-owned state/progress, or configuration files will
  be edited.
- Product implementation files will remain unchanged unless the exact browser validator reveals a
  subsequent error in the same S58-S61 acceptance domain.

## Steps

1. Reproduce the exact strict-locator symptom with the focused S58-S61 Playwright scenario and save
   current-run RED output.
2. Make the smallest test-only repair: require exact account-reference text so the locator selects
   the row rather than the longer checklist heading.
3. Rerun the focused scenario to GREEN and retain the generated
   `closure-readiness-blockers.png`.
4. Rerun the exact slice-specific trusted browser command twice, using independent run-1/run-2
   screenshot directories, and verify both screenshots exist and hash independently.
5. Rerun the exact named validator if an agent-runnable validator entry point exists without
   modifying protected scripts; otherwise retain the two exact command runs for independent
   validation.
6. Update current-run risk assessment and review packet, with Result exactly
   `Ready for independent validation`.
