# Execution Plan

Selected slice: 002F2-navigation-render-regression-tests

## Context Read
- `AGENTS.md`
- `docs/working/TOKEN_RULES.md`
- `docs/working/CONTEXT.md`
- `docs/working/AFK_RUNBOOK.md`
- `.ralph/config.yaml`
- `.ralph/permissions.json`
- `.ralph/state.json`
- `docs/working/HANDOFF.md`
- `docs/working/DECISION_POLICY.md`
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/slices/002F2-navigation-render-regression-tests.md`
- `docs/epics/002-platform-auth-shell.md`
- `docs/slices/002F-role-aware-sidebar-header-navigation.md`
- `docs/working/digests/epic-002-platform-auth.md`

## Permissions Check
- Product/test edits are limited to `sfpcl-lms/src/**`, which is allowed without approval.
- Ralph evidence/status edits are limited to `.ralph/runs/**`, `.ralph/progress.md`, `.ralph/state.json`, `docs/working/**`, and `docs/slices/**`, which are allowed without approval.
- No edits will be made to protected paths, Ralph scripts/config/permissions, `docs/source/**`, or git metadata.

## Plan
1. Add failing frontend unit coverage in `sfpcl-lms/src/services/navigationPermissions.test.ts` for the actual staff-sidebar visibility contract: no-permission users see only Dashboard, tracer-only users see only Dashboard and Tracer, each protected nav item disappears without its required permission, and route guard blocks direct navigation.
2. Extract a small pure helper in `sfpcl-lms/src/services/navigationPermissions.ts` that returns visible staff nav items from the same `can(permission)` predicate used by `Sidebar`.
3. Update `Sidebar.tsx` to consume the helper, preserving the existing nav table, labels, icons, classes, and layout.
4. Run the red test before implementation and save output under `.ralph/runs/2026-07-04_130814_normal_run/evidence/terminal-logs/`.
5. Run frontend gates (`npm test`, `npm run typecheck`, `npm run lint`, `npm run build`) and backend gates with `/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python`; save logs in the run evidence folder.
6. Save changed files, risk assessment, review packet, final summary, update handoff/progress/state/slice status, and sharpen the next Not Started slices using already-opened digest material.
