# Review Packet: 2026-07-03_071656_repair

## Result
Pass

## Slice
002B2-auth-hardening-jwt-library-and-packaging

## Changes
- Added `PyJWT==2.10.1` to `sfpcl_credit/requirements.txt`.
- Replaced custom base64/HMAC JWT encode/decode helpers in `sfpcl_credit/identity/views.py` with `jwt.encode` and `jwt.decode` using HS256.
- Replaced refresh-token hash comparison with `secrets.compare_digest`.
- Read `SECRET_KEY` from `SFPCL_SECRET_KEY`, falling back to the existing local development value.
- Added required regression tests for wrong-secret refresh-token rejection and expired access-token rejection.
- Marked 002B2 complete and sharpened 002C/002D from the existing Epic 002 digest.

## Traceability
- Source/slice says: use an audited JWT library instead of hand-rolled HMAC signing. Code now uses PyJWT HS256 for token issue and verification; `grep -R "hmac" sfpcl_credit/identity/` has no matches.
- Source/slice says: preserve claim set and lifetimes. `access_claims` and `refresh_claims` retain the existing fields and continue to use `AUTH_ACCESS_TOKEN_MINUTES` and `AUTH_REFRESH_TOKEN_HOURS`.
- Source/slice says: `SECRET_KEY` comes from `SFPCL_SECRET_KEY` with the current dev fallback. `sfpcl_credit/config/settings.py` implements exactly that.
- API contract says: login, refresh, and logout use the existing standard envelopes and refresh-session behavior. Response construction was left unchanged, and the existing auth API tests still pass.
- Slice says: wrong-secret and expired access tokens are rejected. Verified by `test_refresh_rejects_token_signed_with_wrong_secret` and `test_expired_access_token_is_rejected`.

## Evidence
- Red evidence: `.ralph/runs/2026-07-03_071656_repair/evidence/terminal-logs/auth-tests-red.log`
- Focused auth tests: `.ralph/runs/2026-07-03_071656_repair/evidence/terminal-logs/auth-tests-green.log`
- Full backend tests: `.ralph/runs/2026-07-03_071656_repair/evidence/terminal-logs/backend-tests.log`
- Backend check: `.ralph/runs/2026-07-03_071656_repair/evidence/terminal-logs/backend-check.log`
- Backend migrations check: `.ralph/runs/2026-07-03_071656_repair/evidence/terminal-logs/backend-migrations.log`
- Backend coverage: `.ralph/runs/2026-07-03_071656_repair/evidence/terminal-logs/backend-coverage.log`
- No-HMAC scan: `.ralph/runs/2026-07-03_071656_repair/evidence/terminal-logs/no-hmac-scan.log`
- Frontend typecheck/tests/build: `.ralph/runs/2026-07-03_071656_repair/typecheck-results.md`, `test-results.md`, `build-results.md`

## Recommended Next Action
Commit this repair work if the sandbox permits git writes, then continue with `002C-role-and-permission-catalogue-seed`.
