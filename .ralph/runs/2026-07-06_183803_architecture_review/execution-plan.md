# Execution Plan

Selected slice: architecture-review

Mode: architecture_review

## Scope
Review the four slices completed since the previous architecture review cadence:
- `003G2-dashboard-internal-auditor-access-regression`
- `003H-dashboard-task-ui-wiring`
- `003I-notification-adapter-shell`
- `003IA-notifications-center-ui-wiring`

## Review Inputs
- Ralph context and guardrails listed in the run prompt.
- The four completed slice files.
- Epic 003 digest and epic file.
- Each reviewed slice's run evidence under `.ralph/runs/`.
- Git diffs for the commits represented by those slices.
- Relevant implementation and tests touched by those commits.

## Steps
1. Establish the reviewed commit range from state/handoff and prior run evidence.
2. Inspect diffs, test files, and run evidence for test quality, source-doc fidelity, duplication, and architecture drift.
3. Spot-check functional requirement traceability for Epic 003 requirements implemented or deferred in the reviewed slices.
4. Append findings, newest first, to `docs/working/REVIEW_FINDINGS.md`; create or sharpen corrective slices for significant issues.
5. Sharpen the next one or two `Not Started` slices using only source extracts already opened/digested.
6. Run validation gates appropriate to a docs-only architecture-review run, save evidence/logs, and update Ralph artifacts/state/handoff.

## Editing Boundaries
- No production code edits.
- No `docs/source/` edits.
- No protected-file edits.
- No git add/commit/push.
