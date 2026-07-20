# Execution Plan

Selected slice: `010H2-interest-calculation-payment-and-replay-owner-closure`

## Repair boundary

- Preserve every existing uncommitted product, migration, and test change from the quarantined
  normal run.
- Fix only the demonstrated cheap-gate failure: the prose following `## Acceptance Evidence` is
  parsed as a malformed table row because that section has no terminating level-two heading.
- Editing is limited to `.ralph/runs/**`, which is allowed by `.ralph/permissions.json`; no
  protected, source, product, slice, state, progress, or handoff file will be changed.

## Feedback loop

Run `ralph_validate_review_finding_closure` directly against the preserved slice and original run
folder. Capture the current malformed-row failure, make the smallest evidence-only correction, then
rerun the exact command and require the recorded malformed-row signal to be absent. If the validator
advances to a different downstream signature, retain it for the orchestrator's bounded progressive
repair rather than expanding this repair beyond its trusted failure summary.

## Evidence and handoff

- Retain the red/green validator outputs under the repair run's `evidence/terminal-logs/` folder.
- Confirm the repaired artifact still maps all seven acceptance IDs and references only retained,
  successful evidence.
- Complete the repair risk assessment, review packet, and final summary. Delegate complete backend,
  PostgreSQL, coverage, and other independent gates to the orchestrator as required for repair mode.
