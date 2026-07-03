# Slice 002C2: Standard API Envelope and Auth Service Boundary

## Status
Complete

## Parent Epic
Epic 002: Platform Auth and Role Shell
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Correct the architecture-review findings from `2026-07-03_081509_architecture_review` before adding `/api/v1/auth/me/`: use one shared API envelope helper and move auth token/session/audit behavior behind explicit module interfaces.

## User Value
Future API slices get consistent response contracts and auth behavior can be tested without piling more workflow logic into Django views.

## Depends On
- 002C

## Concrete Requirements
1. Add a shared backend API response module used by both health and auth endpoints. Success responses must include `success`, `data`, and `meta.request_id`, `meta.timestamp`, `meta.api_version`.
2. Add shared standard error response support matching the implemented auth error shape and the source API contract.
3. Replace the duplicate `success_response` implementations in `sfpcl_credit/ops.py` and `sfpcl_credit/identity/views.py` with the shared helper without changing endpoint URLs, status codes, or response fields except adding the missing `meta.api_version` to health responses.
4. Move auth token/session/audit behavior out of `identity/views.py` into explicit module functions, for example under `sfpcl_credit/identity/modules/` or a similarly local module boundary:
   - issue login tokens and session
   - validate refresh token session
   - rotate refresh token
   - revoke session for logout
   - validate access token for future callers
   - record auth audit events
5. Keep Django views thin: parse HTTP input, call the auth/API modules, and translate known errors to standard responses.
6. Preserve PyJWT HS256, token lifetimes, claims, refresh rotation, replay rejection, logout revocation, inactive-user rejection, and audit behavior from 002B2.

### Concrete starting points (observed 2026-07-03 during 002C)
- Current response helpers to unify: `success_response()` in `sfpcl_credit/ops.py` (health, **missing** `meta.api_version`) and `success_response()` in `sfpcl_credit/identity/views.py` (auth, already includes `api_version`). Put the single helper in a shared module (e.g. `sfpcl_credit/api.py` or `sfpcl_credit/identity/modules/responses.py`) and import it into both.
- Gotcha: `sfpcl_credit/tests/test_auth_api.py` imports `from sfpcl_credit.identity.views import TokenError, decode_token`. When you move token/session logic into the new module, either re-export those names from `views` or update that import in the same slice so the existing suite stays green.
- `settings.AUTH_ACCESS_TOKEN_MINUTES` / `AUTH_REFRESH_TOKEN_HOURS` already exist in `config/settings.py`; the access-token validator you add here is what 002D's `GET /auth/me/` will call.

## Source References
- docs/source/api-contracts.md §6.1-6.4
- docs/source/technical-architecture.md §10, §12, §13.1
- docs/source/codebase-design.md §6-7 and §24 test guidance
- docs/source/auth-permissions.md §5-6

## Prototype Reference
None.

## Screens Involved
None.

## Frontend Scope
None.

## Backend/API Scope
Backend refactor only. No new public endpoint is required.

## Database/Model Impact
None expected.

## API Contracts
Update `docs/working/API_CONTRACTS.md` to note that health and auth endpoints use the same shared envelope helper. Health response examples should show `meta.api_version`.

## Permissions
No new permissions.

## Audit Requirements
Existing auth audit events must remain unchanged. Moving audit creation behind a module boundary must not drop successful/failed login, refresh, or logout audit coverage.

## Validation Rules
The shared envelope helper is the only production response-envelope implementation for current backend endpoints.

## Test Cases
- New test: all health endpoints include `meta.api_version == "v1"`.
- New test: login, refresh, logout, and health responses all use the same standard meta keys.
- New module-level tests cover refresh rotation/replay rejection and logout revocation through the auth module interface, not private view helpers.
- Existing auth API tests and health API tests continue to pass.

## Visual Acceptance Criteria
None.

## Evidence Required
Backend red/green test output, full backend gates, and frontend typecheck/tests/build output.

## Risk Level
High

## Acceptance Criteria
- No duplicated production `success_response` helper remains in `sfpcl_credit/ops.py` or `sfpcl_credit/identity/views.py`.
- Existing auth endpoint contracts are preserved except the deliberate addition of `meta.api_version` where missing.
- Auth views delegate token/session/audit behavior to explicit module functions.
- Backend tests prove the shared envelope and auth module behavior.
- The implementation stays within one small Ralph slice.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated (test_api_envelope.py, test_auth_module.py; existing suites unchanged and green)
- [x] Code implemented (sfpcl_credit/api.py, identity/modules/tokens.py + auth_service.py; ops.py + views.py made thin)
- [x] API contracts updated (API_CONTRACTS.md shared-envelope section; health envelope shows api_version)
- [x] Database rules followed (no model/migration change; makemigrations --check clean)
- [ ] Permissions tested (n/a — no new permissions)
- [x] Audit events tested (record_auth_event covered by module test; login/refresh/logout audit preserved by test_auth_api.py)
- [ ] Visual evidence saved (n/a — no frontend change)
- [x] Tests/typecheck/build passed (backend 33/33, coverage 96%; frontend typecheck/5 tests/build) — lint gate disabled per config
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates (orchestrator commits after independent validation)
