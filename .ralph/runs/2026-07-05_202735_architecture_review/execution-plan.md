# Execution Plan

Selected slice: architecture-review

## Permission Check
- Allowed edit paths from `.ralph/permissions.json`: `.ralph/runs/**`, `docs/working/**`,
  `docs/slices/**`, `.ralph/progress.md`, and `.ralph/state.json`.
- Protected/forbidden paths will not be edited: production code, `scripts/**`, `.ralph/config.yaml`,
  `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/source/**`,
  `docs/working/HIGH_RISK_APPROVALS.md`, `docs/working/DECISION_POLICY.md`, and
  `docs/working/FRONTEND_DESIGN_RULES.md`.

## Review Scope
- Review diffs merged since the prior architecture-review commit `94c437e`.
- Slices in scope: `003D-secure-document-download-with-audit`,
  `003E-versioned-configuration-shell`, `003F-communication-template-shell`, and
  `003G-dashboard-task-summary-api`.

## Steps
1. Read required Ralph context, selected slice state, parent epic, and Epic 003 digest.
2. Inspect reviewed run packets, changed files, tests, API contracts, assumptions, and focused
   backend modules.
3. Critique test quality, doc fidelity, duplication, architecture drift, permissions, audit
   behavior, and functional-spec requirement tracing.
4. Append newest-first findings to `docs/working/REVIEW_FINDINGS.md`.
5. Sharpen the next one or two `Not Started` slice files using source extracts already opened or
   targeted source lookups, and update the Epic 003 digest with any distilled extracts.
6. Run required gates/evidence commands and save logs under
   `.ralph/runs/2026-07-05_202735_architecture_review/evidence/terminal-logs/`.
7. Save `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, `final-summary.md`, update
   `.ralph/progress.md`, `.ralph/state.json`, and `docs/working/HANDOFF.md`.
