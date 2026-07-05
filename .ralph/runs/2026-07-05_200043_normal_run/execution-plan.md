# Execution Plan — 003G Dashboard Task Summary API

## Scope
- Implement only `GET /api/v1/dashboard/`.
- Backend-only slice; no frontend files or screenshots.
- No database models or migrations expected.

## Permission Check
- Editable paths allowed by `.ralph/permissions.json`: `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`, `.ralph/state.json`, `.ralph/progress.md`, and `.ralph/runs/**`.
- Protected/forbidden paths will not be edited: `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/source/**`, and protected working policy docs.

## TDD Plan
1. Add a failing integration-style API test for authorized `GET /api/v1/dashboard/` returning a standard success envelope, `role_context: credit_manager`, zero-count source-named cards, and empty `tasks`.
2. Implement a small dashboard service and thin view, then route `/api/v1/dashboard/`.
3. Add remaining tests for sanctioned role contexts, auth/permission failures, unknown query parameter validation, no audit rows, and no sensitive entity fields.

## Implementation Plan
- Create `sfpcl_credit/dashboard/` with service and view modules, following existing workflow/audit/content-template patterns.
- Use narrow permission `management_readonly` for dashboard summary access, per digest extract from `auth-permissions.md` §19.1; record the assumption because the catalogue has no exact `dashboard.read`.
- Determine `role_context` from the authenticated user's primary role code when it maps to a supported dashboard context; otherwise return the most conservative supported permission-backed context.
- Return only shell card metadata and zero counts for source-named widgets; return `tasks: []`.
- Reject all query parameters with `400 VALIDATION_ERROR`.

## Documentation and Evidence
- Update `docs/working/API_CONTRACTS.md` and `docs/working/ASSUMPTIONS.md`.
- Save red/green test logs, full gate logs, API response example, changed files, risk assessment, review packet, and final summary under `.ralph/runs/2026-07-05_200043_normal_run/`.
- Update `docs/working/HANDOFF.md`, `.ralph/progress.md`, `.ralph/state.json`, and the slice status/checklist.
- Before finish, sharpen the next 1-2 `Not Started` slices only from already-opened digest/source extracts.
