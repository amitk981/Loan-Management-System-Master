# Execution Plan

Selected slice: 006C-loan-limit-configuration-and-calculator

## Repair diagnosis

- The failed `2026-07-10_073133_normal_run` agent could not launch its command runner because
  `/usr/local/bin/codex-code-mode-host` did not exist. It made no product or documentation changes.
- Independent baseline gates passed, but Ralph correctly failed the run for a no-op and unfilled
  artifacts. The leftover worktree contains only its untracked run folder.
- This repair runner is functional, so no failed implementation is being salvaged.

## Implementation plan

1. Inspect the existing loan-application, member fact, versioned loan-policy, permission, audit,
   and workflow seams, plus the source sections explicitly referenced by the selected slice where
   the Epic 006 digest is insufficient.
2. Add a tight API regression test for the missing calculate endpoint and stored lower-of-two
   calculation, run it red with the mandated backend interpreter, and save the output.
3. Add focused tests for eligibility gating, policy ambiguity/missing source facts, member-scope
   validation, amount boundaries/warnings, permissions/object scope/no-evidence behavior, and
   one-to-one rerun updates.
4. Implement the smallest model/migration, service, route/view, permission seed, and policy config
   changes that satisfy the source-backed contract without inventing the unresolved share rule.
5. Re-run focused tests green, update the API contract/digest/assumptions as required, then run all
   backend and frontend quality gates and save self-contained terminal evidence.
6. Sharpen the next one or two Not Started Epic 006 slices using only source material opened during
   this run, then complete the Ralph state, progress, handoff, changed-files, risk, review, and final
   summary artifacts.
