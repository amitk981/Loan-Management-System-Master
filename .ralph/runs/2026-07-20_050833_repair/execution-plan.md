# Repair Execution Plan

## Boundary

Repair only the independently demonstrated backend coverage failure from run
`2026-07-20_041841_normal_run`, preserving the selected slice's existing implementation.

## Steps

1. Build a focused, deterministic reproduction from the five failing migration tests recorded in
   `failure-summary.md`, and retain its output as RED evidence.
2. Rank and test migration-state isolation hypotheses, changing only the minimum slice-owned code or
   tests needed to remove the demonstrated interaction.
3. Re-run the focused reproducer and the selected slice's backend tests with the required Python
   interpreter; retain GREEN evidence.
4. Run proportionate backend checks and migration-sync validation without duplicating the complete
   orchestrator-owned coverage suite.
5. Update the repair run's risk assessment, review packet, and final summary. Set the review result
   exactly to `Ready for independent validation`.

## Guardrails

- No protected files, source documents, frontend files, git metadata, commits, or pushes.
- No expansion of slice 010E2 behavior; the repair is limited to the recorded migration-test gate
  failure.
- The orchestrator remains responsible for full independent coverage revalidation and mechanical
  bookkeeping.
