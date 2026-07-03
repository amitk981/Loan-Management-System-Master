# Review Packet: 2026-07-03_065754_normal_run

## Result
Pass

## Slice
002B2-auth-hardening-jwt-library-and-packaging

## Changes
- Added `PyJWT==2.10.1` to `sfpcl_credit/requirements.txt`.
- Replaced hand-rolled JWT base64/HMAC encode/decode helpers in `sfpcl_credit/identity/views.py` with PyJWT HS256 encode/decode.
- Switched refresh-token hash comparison to `secrets.compare_digest`.
- Read Django `SECRET_KEY` from `SFPCL_SECRET_KEY`, falling back to the existing local development value.
- Added auth regression tests for wrong-secret refresh rejection and expired access-token rejection.
- Sharpened the next two not-started slices, 002C and 002D, from the Epic 002 digest.

## Traceability
- Slice requirement: use PyJWT HS256 while preserving claims and token lifetimes. Code now issues `jwt.encode(..., algorithm="HS256")`, decodes with `algorithms=["HS256"]`, and keeps `access_claims`, `refresh_claims`, and configured lifetimes unchanged.
- Slice requirement: secret comes from `SFPCL_SECRET_KEY` with dev fallback. `sfpcl_credit/config/settings.py` now reads that environment variable.
- Slice requirement: contracts stay byte-for-byte compatible. Login, refresh, and logout response construction was not changed; existing auth API tests still pass.
- Slice requirement: refresh rotation, replay rejection, and logout revocation remain unchanged. Existing tests for refresh rotation/replay and logout revocation still pass.
- Slice requirement: wrong-secret and expired access tokens are rejected. Verified by `test_refresh_rejects_token_signed_with_wrong_secret` and `test_expired_access_token_is_rejected`.

## Evidence
- Red evidence: `.ralph/runs/2026-07-03_065754_normal_run/evidence/terminal-logs/auth-tests-red.log`
- Focused green auth tests: `.ralph/runs/2026-07-03_065754_normal_run/evidence/terminal-logs/auth-tests-green.log`
- Backend tests/check/migrations/coverage: `.ralph/runs/2026-07-03_065754_normal_run/evidence/terminal-logs/backend-*.log`
- Frontend typecheck/tests/build: `.ralph/runs/2026-07-03_065754_normal_run/evidence/terminal-logs/frontend-*.log`
- No-HMAC scan: `.ralph/runs/2026-07-03_065754_normal_run/evidence/terminal-logs/no-hmac-scan.log`

## Recommended Next Action
Commit this validated work from an environment with `.git/worktrees` write permission, then proceed to 002C-role-and-permission-catalogue-seed.
