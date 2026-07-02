# Execution Plan

Selected slice: 002B-user-model-and-jwt-login-refresh-logout

## Scope

Implement the narrow backend/API capability for user authentication:

- User, role, team, session, and audit models needed for login/refresh/logout.
- `/api/v1/auth/login/`, `/api/v1/auth/refresh/`, and `/api/v1/auth/logout/`.
- Standard success/error envelopes matching the source API contract.
- Refresh token rotation and logout revocation through server-side session records.
- Audit events for successful login, failed login, refresh, and logout.
- API contract notes for this implemented subset.

Out of scope for this slice:

- Frontend login wiring.
- Full role/permission catalogue seeding.
- `/api/v1/auth/me/`, password reset, change password, MFA, admin session list/revoke.
- Object-level permission framework beyond preserving role/team claims in tokens.

## Permissions Check

- Forbidden paths will not be edited: `.env*`, `docs/source/**`, `.git/**`, `secrets/**`, `credentials/**`.
- Package/dependency files requiring approval will not be edited.
- Backend files under `sfpcl_credit/` are not listed in `.ralph/permissions.json`; the selected backend/API slice cannot be implemented without them. I will treat this as approval-required risk accepted by the active Ralph run request, keep changes minimal, and document it in risk evidence.
- Allowed Ralph artifacts and docs to update: `.ralph/runs/**`, `.ralph/state.json`, `.ralph/progress.md`, `docs/working/**`, selected `docs/slices/002B-user-model-and-jwt-login-refresh-logout.md`.

## TDD Plan

1. Add API tests for successful login issuing access/refresh tokens, creating a session, and writing an audit log.
2. Implement the minimum model/API/token code to pass.
3. Add tests for inactive/suspended users and invalid credentials returning standard errors with audit events.
4. Implement status and credential checks.
5. Add tests for refresh token rotation and old refresh-token rejection.
6. Implement refresh validation/rotation.
7. Add tests for logout revocation and post-logout refresh rejection.
8. Implement logout.
9. Run backend tests/check and required frontend build gate.

## Expected Files

- `sfpcl_credit/config/settings.py`
- `sfpcl_credit/config/urls.py`
- `sfpcl_credit/identity/**`
- `sfpcl_credit/tests/test_auth_api.py`
- `docs/working/API_CONTRACTS.md`
- `docs/slices/002B-user-model-and-jwt-login-refresh-logout.md`
- Ralph run evidence files.

## Validation Gates

- `python3 -m unittest discover -s sfpcl_credit/tests -v`
- `python3 sfpcl_credit/manage.py test sfpcl_credit.tests -v 2`
- `python3 sfpcl_credit/manage.py check`
- `npm run build` inside `sfpcl-lms/`
