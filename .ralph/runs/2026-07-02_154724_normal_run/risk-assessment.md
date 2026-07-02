# Risk Assessment

Risk level: High

- Selected slice: 002B-user-model-and-jwt-login-refresh-logout
- Mode: normal_run
- Manual review required: yes

## Risk Drivers

- Authentication/session code is security-sensitive.
- The run used no new dependencies because `.ralph/config.yaml` sets `max_new_dependencies: 0`; tokens are local HMAC-signed JWTs instead of PyJWT/DRF Simple JWT.
- Backend files under `sfpcl_credit/` are not explicitly listed in `.ralph/permissions.json`, but this selected backend/API slice cannot be implemented without them.
- No production database dependency file or migration package exists yet; Django syncs the unmigrated identity app in tests.
- Frontend build required `npm ci` because this worktree lacked `node_modules`; install succeeded from the lockfile with Node 18 engine warnings for React Router's Node 20 requirement.

## Mitigations

- Kept scope limited to login, refresh, logout, and supporting auth/session/audit models.
- Added API-level tests for active-user login, invalid credentials, inactive user denial, refresh rotation/replay rejection, and logout revocation.
- Stored only refresh-token hashes in `user_sessions`.
- Included minimal token claims and excluded sensitive personal/financial data.
- Recorded provisional dependency/JWT assumption in `docs/working/ASSUMPTIONS.md`.

## Residual Risk

- Replace local token implementation with an approved JWT library once dependency policy allows.
- Add migrations/packaging in a dedicated backend infrastructure slice.
- Add rate limiting, CSRF/cookie strategy, current-user API, permission catalogue, and admin session controls in future slices.
