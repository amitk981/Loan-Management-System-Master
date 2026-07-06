# Execution Plan

Selected slice: 003H-dashboard-task-ui-wiring

## Scope
- Wire the existing staff Dashboard page to `GET /api/v1/dashboard/` using the implemented 003G contract in `docs/working/API_CONTRACTS.md`.
- Preserve existing dashboard layout/card/list/alert classes and component patterns; no new styling, colours, or visual components.
- Keep backend behavior unchanged.

## Steps
1. Add frontend tests first for the dashboard API client/rendering path:
   - loading/success cards from mocked `/api/v1/dashboard/`
   - empty `tasks: []` state
   - `401`/`403` and network/server error states
   - role contexts `credit_manager`, `sanction_committee`, `compliance`, `treasury`, and `management`
2. Implement a small dashboard API client that reads the stored bearer session, calls `/api/v1/dashboard/`, and raises existing `AuthSessionError` failures.
3. Replace the Dashboard mock summary/task rendering with the API summary while reusing `KPICard`, `AlertBanner`, and existing empty-list/card patterns.
4. Run focused frontend tests after each red/green step, then full frontend gates and backend gates.
5. Save visual screenshots for loading/success/error/unauthorized states and required Ralph evidence artifacts.
6. Update run documents, handoff/progress/state/slice status, and sharpen the next `Not Started` slices from already-opened epic/digest context.

## Permission Check
- Allowed edit paths needed for this run: `sfpcl-lms/src/**`, `.ralph/runs/**`, `docs/working/**`, `.ralph/state.json`, `.ralph/progress.md`, and `docs/slices/**`.
- Protected/read-only paths will not be edited: `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/working/HIGH_RISK_APPROVALS.md`, `docs/working/DECISION_POLICY.md`, `docs/working/FRONTEND_DESIGN_RULES.md`, and `docs/source/**`.
