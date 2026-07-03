# Execution Plan — 002E Protected Frontend Route Shell

## Scope
- Replace staff demo login/session state with backend-backed login, `/auth/me/` current-user loading, token persistence, and logout.
- Preserve borrower portal demo auth flow.
- Preserve the existing frontend visual system exactly; change labels/state/data wiring only.
- Keep backend endpoints unchanged.

## Permission Check
Allowed editable paths for this slice:
- `sfpcl-lms/src/**`
- `docs/working/**`
- `docs/slices/**`
- `.ralph/state.json`
- `.ralph/progress.md`
- `.ralph/runs/**`

Protected/forbidden paths will not be modified:
- `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`
- `docs/working/HIGH_RISK_APPROVALS.md`, `docs/working/DECISION_POLICY.md`, `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/source/**`, `.git/**`

## Steps
1. Add failing frontend tests for:
   - login posts credentials, stores tokens, calls `/api/v1/auth/me/`, and returns current user state.
   - role/team display uses `/auth/me/` `roles`/`teams`; `role_codes`/`team_codes` are derived compatibility fields.
   - invalid login does not create a session.
   - `TOKEN_EXPIRED`/`INVALID_TOKEN` current-user failure clears stored auth.
   - logout posts `refresh_token`, clears auth, and returns to login state.
   - backend canonical permissions map to existing prototype permissions without granting unknown codes.
2. Implement a small frontend auth API/session module using the existing `/api/v1/auth/login/`, `/logout/`, and `/me/` contracts.
3. Update `RoleContext` so staff user, role/team display, compatibility role/team codes, permissions, and `can(...)` derive from the backend current-user payload. Keep demo role switching only when `VITE_ENABLE_DEMO_AUTH === "true"`.
4. Update `LoginScreen`, `App`, `Header`, and `Sidebar` wiring without changing the visual design.
5. Add existing-pattern loading, invalid-login, expired-session, unauthorized/blocked, and logout states.
6. Save evidence:
   - red/green frontend test logs under `.ralph/runs/2026-07-03_222318_normal_run/evidence/terminal-logs/`.
   - frontend typecheck/test/build logs.
   - backend check/test/migration/coverage logs with the required Ralph venv interpreter.
   - screenshots and API/CORS smoke evidence where possible.
7. Update working docs/artifacts:
   - `docs/working/API_CONTRACTS.md` only if a frontend integration note is needed.
   - `docs/working/ASSUMPTIONS.md` for unresolved permission mapping assumptions.
   - sharpen the next 1-2 Not Started slice files using only opened source/digest context.
   - update handoff, progress, state, selected slice status, changed files, risk assessment, review packet, and final summary.

## Risk
Medium. The slice changes frontend authentication/session state and route/sidebar authorization, but does not alter backend auth behavior or database models.
