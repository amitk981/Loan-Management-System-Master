# Slice 002E: Protected Frontend Route Shell

## Status
Complete

## Parent Epic
Epic 002: Platform Auth and Role Shell
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Replace the demo-only staff auth shell with a protected frontend session path backed by the real auth APIs from 002B-002D.

## User Value
Staff users sign in through the real backend, the app shell loads the current backend session, and protected screens no longer depend on a mock role dropdown for access decisions.

## Depends On
- 002D
- 002D2
- 002D3

## Source References
- docs/source/implementation-roadmap.md sections 10, 20-22
- docs/source/technical-architecture.md sections 8-12, 17-18
- docs/source/auth-permissions.md
- docs/source/api-contracts.md sections 11-12, 43-44
- docs/source/data-model.md identity/access tables

## Prototype Reference
- sfpcl-lms/src/pages/auth/LoginScreen.tsx
- sfpcl-lms/src/pages/Dashboard.tsx
- sfpcl-lms/src/components/layout/*
- sfpcl-lms/src/contexts/RoleContext.tsx

## Screens Involved
- Staff login (`LoginScreen`)
- Staff app shell (`AppShell`, `Header`, `Sidebar`)
- Dashboard/unauthorized fallback within the existing dashboard shell
- No borrower portal wiring in this slice

## Frontend Scope
- Add a small API client for the implemented auth endpoints: `POST /api/v1/auth/login/`, `POST /api/v1/auth/logout/`, and `GET /api/v1/auth/me/`.
- Use the 002D2 development backend contract: API base URL defaults to `http://127.0.0.1:8000`, Vite runs on `http://localhost:5173`, and CORS must succeed without a frontend proxy for health/auth calls.
- Replace `AppInner`'s local demo `isLoggedIn` + `handleLogin(role)` flow for staff with real email/password login, token storage, current-user loading, and logout.
- Keep the existing visual design exactly. Reuse `LoginScreen`, `AppShell`, `AlertBanner`/existing alert styles, `Sidebar`, and `Header`; change labels/state wiring only.
- Remove or gate the staff demo role selector behind an explicit development flag such as `import.meta.env.VITE_ENABLE_DEMO_AUTH === "true"`; production/default behavior must use the backend login API.
- Update `RoleContext` so `currentUser`, role/team display data, `role_codes`, `team_codes`, `permissions`, and `can(...)` are derived from `/api/v1/auth/me/` for staff sessions. The existing prototype permission strings may remain as a mapping layer, but the backend canonical permission codes are the source of truth.
- Treat `/api/v1/auth/me/` `roles` and `teams` objects as the display source for role/team names. Treat `role_codes` and `team_codes` as compatibility fields only; tests must assert they match the object arrays rather than becoming a separate source of truth.
- Add loading, invalid-credentials, expired/invalid-session, unauthorized, and logout states using existing patterns. No new colours, card styles, typography, or layouts.
- Preserve borrower portal demo auth flow for now; member portal production auth is deferred to 005FA.

## Backend/API Scope
No new backend endpoints. Use the already implemented auth API:
- `POST /api/v1/auth/login/` returns bearer `access_token`, `refresh_token`, `expires_in`, and user profile.
- `GET /api/v1/auth/me/` requires `Authorization: Bearer <access_token>` and, after 002D3, returns `user_id`, `full_name`, `email`, `mobile_number`, `status`, `roles[{role_code, role_name}]`, `teams[{team_code, team_name}]`, `role_codes`, `team_codes`, sorted `permissions`, and `available_actions`.
- `POST /api/v1/auth/logout/` takes `refresh_token` and revokes the session.

## Database/Model Impact
None.

## API Contracts
Update `docs/working/API_CONTRACTS.md` only if the frontend needs an integration note. Do not change backend response shapes in this slice; 002D3 owns `/auth/me/` contract correction.

## Permissions
Frontend hiding is convenience only. For staff shell navigation:
- Use `/auth/me/` `permissions`/`available_actions` as the backend session source.
- Map canonical backend permission codes to the existing route visibility checks in `PAGE_PERMISSIONS` and `Sidebar` without inventing grants. Examples from the current backend/prototype bridge: `reports.export` enables export/report affordances; `finance.loan_account.read` maps to existing loan-account viewing checks.
- A-007 roles with zero backend permission links (`sales_team_user`, `it_head`, `management_viewer`) must see only routes whose permissions are absent/unrestricted, until source docs define grants.
- Unknown permission needs must be recorded in `ASSUMPTIONS.md`, not guessed.

## Audit Requirements
No new frontend audit event. Login/logout audit is already handled by backend endpoints from prior slices.

## Validation Rules
- Missing backend session shows `LoginScreen`.
- Bad credentials show the existing login error style and do not enter the app shell.
- A missing/expired/invalid `/auth/me/` response clears local auth state and returns to login.
- A successful login must load `/auth/me/` before rendering staff navigation.
- Staff pages protected by permissions should redirect/fallback to the existing dashboard unauthorized/blocked pattern rather than exposing the page.

## Test Cases
- Frontend test: login form posts credentials to `/api/v1/auth/login/`, then calls `/api/v1/auth/me/`, then renders the dashboard shell with backend user name/role-derived state.
- Frontend test: role/team display uses `/auth/me/` `roles`/`teams` objects when present, while permission checks use canonical `permissions`.
- Frontend test: `role_codes` and `team_codes` remain available to legacy route/sidebar checks and match `/auth/me/` `roles[*].role_code` and `teams[*].team_code`.
- Frontend test: invalid login response displays the existing error state and does not render `AppShell`.
- Frontend test: `/api/v1/auth/me/` `401 TOKEN_EXPIRED` or `INVALID_TOKEN` clears auth state and shows login.
- Frontend test: navigation hides or blocks a route when the backend permission list does not include the mapped permission.
- Frontend test: logout calls `/api/v1/auth/logout/` with the refresh token and returns to login.
- Backend tests remain green; no backend behavior changes expected.
- Integration smoke: with a migrated persistent dev DB, login and `/auth/me/` work across separate browser/API requests after a page reload.

## Visual Acceptance Criteria
Screens must be visually indistinguishable from the prototype:
- `LoginScreen` keeps the same layout, logo, colours, typography, inputs, and button styling.
- Loading/error/unauthorized states reuse existing alert and dashboard patterns.
- No new component library, colour, spacing, card, badge, or table pattern.
- Save screenshots for login, loading/current-user fetch, authenticated dashboard, invalid login, and unauthorized/permission-blocked navigation.

## Evidence Required
- Frontend test/typecheck/build logs.
- Backend check/tests/migrations/coverage logs to prove auth endpoints still pass.
- Screenshots for the visual states above.
- API interaction evidence showing login → me → logout in development.
- CORS evidence for `GET /api/v1/health/live/` or auth from `Origin: http://localhost:5173`.

## Risk Level
Medium

## Acceptance Criteria
- Staff login uses real backend auth by default.
- The protected shell renders only after `/api/v1/auth/me/` succeeds.
- Route/sidebar permission decisions come from backend current-user permissions through a documented mapping layer.
- Invalid, expired, or revoked sessions return the user to login without exposing protected content.
- Existing borrower portal demo remains functional and untouched except for shared compile fixes if needed.
- All gates pass and screenshots are saved.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated, if needed
- [x] Database rules followed, if needed
- [x] Permissions tested, if needed
- [x] Audit events tested, if needed
- [x] Visual evidence saved, if frontend
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates
