# Review Packet: 2026-07-03_073118_normal_run

## Result
Failed / blocked by backend dependency environment

## Slice
002B2-auth-hardening-jwt-library-and-packaging

## Summary
- Added `PyJWT==2.10.1`.
- Replaced custom JWT HMAC/base64 signing with `jwt.encode` / `jwt.decode` using HS256.
- Switched Django `SECRET_KEY` to `SFPCL_SECRET_KEY` with the previous local dev value as fallback.
- Kept auth endpoint request/response shapes unchanged.
- Added tests for wrong-secret refresh-token rejection and expired access-token rejection.

## Traceability
- Slice requirement: replace custom signing with PyJWT while preserving claims and lifetimes. Code now uses `encode_token()` / `decode_token()` around PyJWT and leaves `access_claims()` / `refresh_claims()` unchanged.
- Slice requirement: wrong-secret token rejected. Test added: `AuthApiTests.test_refresh_token_signed_with_wrong_secret_is_rejected`.
- Slice requirement: expired access token rejected. Test added: `AuthApiTests.test_expired_access_token_is_rejected`.
- Slice requirement: no hand-rolled HMAC remains. Evidence: `evidence/terminal-logs/grep-hmac.log`.
- Contract requirement: login/refresh/logout shapes unchanged. Endpoint handlers and `auth_payload()` / `success_response()` / `error_response()` were not structurally changed.

## Evidence
- RED evidence: `evidence/terminal-logs/red-wrong-secret-token.log` (blocked at missing baseline Django package after test was added).
- Backend dependency install attempt: `evidence/terminal-logs/install-baseline-backend-deps.log` (failed: no package-index network access).
- Syntax check: `evidence/terminal-logs/python-compileall.log` (passed).
- No-HMAC check: `evidence/terminal-logs/grep-hmac.log` (passed).
- Backend gates: `backend-check.log`, `backend-auth-tests.log`, `backend-migrations-check.log`, `backend-coverage.log` (blocked by missing Django/coverage).
- Frontend gates: `frontend-typecheck.log`, `frontend-tests.log`, `frontend-build.log` (passed after `frontend-install.log`).

## Recommended Next Action
Repair/revalidate after backend Python dependencies are available. Do not merge until backend check/tests/migration/coverage gates pass.
