# Execution Plan

Selected slice: architecture-review

Mode: architecture_review

## Scope
Review the four completed slices since the last architecture review:
- `005C2-application-object-access-hardening`
- `005D-application-document-checklist`
- `005E-completeness-workbench`
- `005F-deficiency-creation-and-resolution`

No production code will be modified.

## Plan
1. Confirm the diff window from state, review findings, run evidence, and git history.
2. Inspect the product diffs and run evidence for the four reviewed slices.
3. Critique test quality, source/doc fidelity, duplication, and architecture drift.
4. Spot-check Epic 005 functional requirements that are implemented or explicitly deferred.
5. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`.
6. Create or sharpen corrective slices for any significant issue, then sharpen the next 1-2 `Not Started` slices using requirements already opened.
7. Save architecture-review artifacts: evidence logs, `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.
8. Update `.ralph/state.json`, `.ralph/progress.md`, `docs/working/HANDOFF.md`, and the virtual architecture-review status.

## Permission Check
Allowed edit targets from `.ralph/permissions.json`:
- `.ralph/runs/**`
- `docs/working/**`
- `docs/slices/**`
- `.ralph/progress.md`
- `.ralph/state.json`

Forbidden/protected targets will not be edited:
- `docs/source/**`
- `scripts/**`
- `.ralph/config.yaml`
- `.ralph/permissions.json`
- `AGENTS.md`
- `CLAUDE.md`
- `.gitignore`
- `docs/working/HIGH_RISK_APPROVALS.md`
- `docs/working/DECISION_POLICY.md`
- `docs/working/FRONTEND_DESIGN_RULES.md`
