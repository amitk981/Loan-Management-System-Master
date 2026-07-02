# Slice 002B2: Auth Hardening — Replace Hand-Rolled JWT with PyJWT

## Status
Not Started

## Parent Epic
Epic 002: Platform Auth and Role Shell
Epic file: `docs/epics/002-platform-auth-shell.md`

## Goal
Remove the security debt created in slice 002B: the token signing in `sfpcl_credit/identity/views.py` was hand-implemented with HMAC because the dependency policy blocked libraries at the time. Replace it with the standard PyJWT library and move the secret out of source code.

## User Value
Login security rests on an audited, widely-used library instead of custom cryptography, before any real user data exists.

## Depends On
- 002B

## Concrete Requirements
1. Add `PyJWT` (pinned) to `sfpcl_credit/requirements.txt`; install and verify import.
2. Replace the custom HMAC token encode/decode in `sfpcl_credit/identity/views.py` with `jwt.encode` / `jwt.decode` (HS256), preserving the existing claim set (user id, expiry) and token lifetimes from `settings.AUTH_ACCESS_TOKEN_MINUTES` / `AUTH_REFRESH_TOKEN_HOURS`.
3. Read `SECRET_KEY` from the `SFPCL_SECRET_KEY` environment variable with the current dev value as fallback; never log it.
4. Keep the API contract for `POST /api/v1/auth/login/`, `/refresh/`, `/logout/` byte-for-byte compatible (same request/response fields, same error shapes) — see `docs/working/API_CONTRACTS.md`.
5. Refresh-session storage, rotation, replay rejection, and logout revocation behaviour must not change.

## Test Cases
- All existing tests in `sfpcl_credit/tests/test_auth_api.py` pass unchanged.
- New test: a token signed with a wrong secret is rejected.
- New test: an expired access token is rejected.

## Out of Scope
Rate limiting, cookies/CSRF strategy, password policy, DRF adoption.

## Risk Level
High

## Acceptance Criteria
- No hand-rolled signing/verification code remains in `sfpcl_credit/`.
- `grep -r "hmac" sfpcl_credit/identity/` returns nothing (or only PyJWT internals via imports).
- All gates pass (backend tests/check, frontend typecheck/tests/build).

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts confirmed unchanged
- [ ] Tests/typecheck/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
