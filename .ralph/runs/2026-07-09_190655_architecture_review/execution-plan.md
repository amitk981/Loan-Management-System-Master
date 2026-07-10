# Execution Plan

Selected slice: architecture-review

## Scope
- Architecture-review mode only: do not modify production code, migrations, frontend source, backend source, dependencies, protected files, or `docs/source/**`.
- Review the four completed slices since the last architecture review cadence window:
  `004K2-borrower-360-bank-holder-contract-hardening`,
  `005A-loan-application-draft-create-update`,
  `005B-application-submit-and-status-transition`, and
  `005C-reference-number-generation-and-loan-request-register`.
- Use slice files, parent epics, existing digests, prior run artifacts, and git diffs as the spec/evidence base.

## Plan
1. Identify the prior architecture-review commit and capture the commit list/diff for the review window.
2. Inspect changed files, tests, migrations, API contracts, assumptions, evidence packets, and run summaries for the four completed slices.
3. Critique test quality, doc/source fidelity, sensitive-data boundaries, duplication, and architecture drift.
4. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`.
5. Create or sharpen corrective/follow-up slices only for significant findings; otherwise sharpen the next one or two `Not Started` slices using the already-opened digest/source context.
6. Run required quality gates and save terminal evidence in `.ralph/runs/2026-07-09_190655_architecture_review/evidence/terminal-logs/`.
7. Save `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, `final-summary.md`; update `.ralph/state.json`, `.ralph/progress.md`, and `docs/working/HANDOFF.md`.

## Permissions Checked
- Allowed edit paths: `.ralph/runs/**`, `docs/working/**`, `docs/slices/**`, `.ralph/progress.md`, `.ralph/state.json`.
- Forbidden/protected paths will not be edited: production code, `docs/source/**`, scripts, Ralph config/permissions, AGENTS/CLAUDE, git metadata, and risk/policy guardrails.
