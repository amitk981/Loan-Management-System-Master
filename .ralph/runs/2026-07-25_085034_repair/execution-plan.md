# Execution Plan

Selected slice: 012G-critical-e2e-uat-smoke-scenarios

Mode: same-worktree repair

## Authoritative Failure

The trusted browser validator launched Chromium and reached
`UAT-014/015/016/017: direct/subsidiary receipts, interest, DPD, and replay safety`.
The scenario expected HTTP 200 but received HTTP 409. Screenshot evidence is incomplete only
because this post-launch application assertion stopped the first run.

## Permission Check

- Read `.ralph/permissions.json` before editing.
- Candidate paths already in scope are under `sfpcl-lms/**`, `sfpcl_credit/**`, and this run's
  `.ralph/runs/2026-07-25_085034_repair/**`; all are allowed without interactive approval.
- Protected and forbidden paths, including `scripts/**`, `.ralph/config.yaml`,
  `.ralph/permissions.json`, workflow policy files, and `docs/source/**`, will not be edited.
- Git metadata and orchestrator-owned state/progress/status files will not be edited.

## Repair Steps

1. [completed] Inspect the full trusted-browser log around the 409 and the current critical UAT spec/seed
   candidate to identify the exact public request and replay expectation.
2. [completed] Establish a focused, deterministic red-capable reproduction for that request and save its
   output under this run's `evidence/terminal-logs/`.
3. [completed] Rank and test bounded hypotheses about seed preconditions, request identity, and public API
   replay semantics. Change only the demonstrated browser/seed contract domain.
4. [completed] Add one focused failing public behavior test before the fixture repair,
   retain red/green logs, and use the mandated Ralph venv for every backend command.
5. [completed] Rerun focused frontend/backend checks affected by the repair and rerun the exact
   browser validator. Both post-fix browser attempts ended before page creation due to Chrome
   launch infrastructure; preserve the logs and leave screenshot acceptance to trusted validation.
6. [completed] Save the diagnosis, focused test outputs, risk assessment, review packet, and final summary.
   Set the review packet result exactly to `Ready for independent validation`.

## Stop Conditions

Stop only for a protected/forbidden edit, an unsafe git state, a repeated same-gate failure after
the bounded repair, or a diff-limit breach. Do not broaden into unrelated product defects.
