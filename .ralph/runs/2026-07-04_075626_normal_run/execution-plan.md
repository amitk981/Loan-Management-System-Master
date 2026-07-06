# Execution Plan

Selected slice: 002F-role-aware-sidebar-header-navigation

## Scope
- Verify and tighten the existing staff shell navigation permission bridge only.
- Touch frontend auth/session, route guard, sidebar/header tests or logic only if the tests expose a real gap.
- No backend, database, dependency, colour, typography, layout, or new component work is planned.

## Source Trace
- Slice: `docs/slices/002F-role-aware-sidebar-header-navigation.md`
- Parent epic: `docs/epics/002-platform-auth-shell.md`
- Digest: `docs/working/digests/epic-002-platform-auth.md`
- Relevant source extracts from digest:
  - `/auth/me/` exposes roles, teams, permissions, and available actions.
  - React UX derives visibility from explicit backend canonical permissions mapped to prototype permissions.
  - Unknown permission mappings grant no UI access.
  - Zero-permission/unmapped backend roles map to neutral `backend_staff`.

## Edit Permission Check
- Allowed paths likely needed: `sfpcl-lms/src/**`, `docs/working/**`, `docs/slices/**`, `.ralph/progress.md`, `.ralph/state.json`, `.ralph/runs/**`.
- Protected/forbidden paths will not be edited: `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/source/**`, `docs/working/HIGH_RISK_APPROVALS.md`, `docs/working/DECISION_POLICY.md`, `docs/working/FRONTEND_DESIGN_RULES.md`.

## Test-First Plan
1. Inspect the existing frontend shell implementation and test harness.
2. Add failing frontend tests for:
   - every sidebar nav item hides without its `requiredPermission`;
   - route guard blocks direct navigation to protected pages and shows the amber access-blocked dashboard banner;
   - `tracer.lifecycle.run` maps only to `run_tracer` and unlocks no other prototype permissions;
   - zero-permission `backend_staff`, `it_head`, `management_viewer`, unknown role code, and empty permission sessions expose only Dashboard and no Settings shortcut;
   - revoked/invalid stored session restore clears auth and returns to the staff login before protected shell items render.
3. Run the targeted frontend test command and save red output under `evidence/terminal-logs/`.
4. Implement the smallest frontend logic or export changes needed to make the tests pass.
5. Re-run targeted tests, then full Ralph gates: frontend test/typecheck/build and backend check/tests/migrations/coverage using the required venv interpreter.
6. Save evidence, screenshots or visual notes for touched frontend states, changed-files, risk assessment, review packet, final summary, and update state/progress/handoff/slice status.
7. Sharpen the next one or two `Not Started` slice files using only already-read epic/digest context.
