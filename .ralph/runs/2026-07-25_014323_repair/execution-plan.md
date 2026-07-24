# Execution Plan

Selected slice: 011PC-closure-frontend-wiring

## Repair Boundary

Repair only the demonstrated Ralph artifact-quality validation domain for the preserved 011PC
candidate. The immediately preceding repair failed its cheap checks because this run's execution
plan and risk assessment were untouched templates and its review packet still declared
`In Progress`. Product code, tests, browser contracts, source documents, queue state, slice status,
and prior-run evidence are outside this repair boundary.

## Plan

1. Preserve the existing candidate and use the prior `failure-summary.md` plus the exact artifact
   checker as the tight red/green feedback loop.
2. Replace the current run's execution-plan and risk-assessment templates with self-contained,
   slice-specific repair evidence.
3. Complete the current review packet with the exact result `Ready for independent validation`,
   explaining the bounded repair, inherited product/browser evidence, and independent-validation
   requirement.
4. Complete the final summary consistently and scan the four agent-owned artifacts for template or
   incomplete-result markers.
5. Rerun the exact named artifact-quality and agent-declared-result validator until it passes.
   Save the validator output in the current run folder and leave full product/browser revalidation
   to the orchestrator.

## Permissions Check

- Allowed repair writes: `.ralph/runs/2026-07-25_014323_repair/**`.
- Preserved candidate paths, prior run folders, product code, tests, and E2E specifications remain
  unchanged.
- Protected and forbidden paths remain read-only, including `scripts/**`, `.ralph/config.yaml`,
  `.ralph/permissions.json`, `.codex/config.toml`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`,
  `docs/source/**`, and binding decision/design policy files.
- No git add, commit, push, dependency install, backend command, state/progress update, slice status
  change, or mechanical handoff edit is authorized.
