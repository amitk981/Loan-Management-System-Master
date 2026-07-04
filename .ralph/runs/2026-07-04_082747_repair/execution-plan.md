# Execution Plan

Selected slice: 002FL-frontend-lint-baseline

Mode: repair

## Failure Diagnosis
- Newest failed/leftover worktree inspected: `../2026-07-04_080756_normal_run`.
- That attempt produced implementation changes and green local gate evidence, but the Ralph run artifacts retained placeholder `In Progress` headers and artifact validation ended with an unexplained `Validation failed with 2 issue(s)` summary. The current repair will redo the slice in this worktree and produce complete, final artifacts.
- Do not copy ungated work from the leftover worktree.

## Permission Check
- Allowed edit paths for this slice: `sfpcl-lms/src/**`, `sfpcl-lms/package.json`, `sfpcl-lms/package-lock.json`, `sfpcl-lms/eslint.config.js`, `docs/working/**`, `docs/slices/**`, `.ralph/progress.md`, `.ralph/state.json`, `.ralph/runs/**`.
- Protected/forbidden paths will not be edited: `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/working/HIGH_RISK_APPROVALS.md`, `docs/working/DECISION_POLICY.md`, `docs/working/FRONTEND_DESIGN_RULES.md`, `docs/source/**`, `.git/**`.

## Plan
1. Add pinned approved frontend lint dependencies and `npm run lint` to `sfpcl-lms/package.json`; update the lockfile without adding unapproved packages.
2. Add `sfpcl-lms/eslint.config.js` using flat ESLint config with recommended JavaScript, TypeScript, React Hooks, and React Refresh rules, scoped to `src`.
3. Run `npm run lint` as the red-capable feedback loop and save evidence.
4. Fix lint violations in `sfpcl-lms/src` only with syntax/import/hook-dependency cleanup that does not alter labels, styling, navigation tables, permissions, or visual behavior.
5. Re-run `npm run lint`, `npm run typecheck`, `npm test`, `npm run build`, and backend gates with `/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python`.
6. Save final evidence, changed files, risk assessment, review packet, final summary, and update state/progress/handoff/slice status. Record the protected lint-gate flip request in `HANDOFF.md`.
7. Sharpen the next 1-2 `Not Started` slice files using only already-opened Epic 002/digest context.
