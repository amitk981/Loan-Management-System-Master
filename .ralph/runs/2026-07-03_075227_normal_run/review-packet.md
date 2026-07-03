# Review Packet: 2026-07-03_075227_normal_run

## Result
Code complete; local validation blocked by missing installed dependencies.

## Slice
002B2-auth-hardening-jwt-library-and-packaging

## Traceability
- Slice requirement: add pinned PyJWT. Code: `sfpcl_credit/requirements.txt` pins `PyJWT==2.10.1`.
- Slice requirement: replace custom HMAC token encode/decode with PyJWT HS256. Code: `sfpcl_credit/identity/views.py` uses `jwt.encode` and `jwt.decode`; `rg "hmac" sfpcl_credit/identity` has no matches.
- Slice requirement: preserve claim set and lifetimes. Code: `access_claims()` and `refresh_claims()` remain the source of token claims and still use `AUTH_ACCESS_TOKEN_MINUTES` / `AUTH_REFRESH_TOKEN_HOURS`.
- Slice requirement: read `SECRET_KEY` from `SFPCL_SECRET_KEY` with dev fallback. Code: `sfpcl_credit/config/settings.py`; test: `AuthSettingsTests.test_secret_key_can_be_read_from_environment`.
- Slice requirement: keep auth API contract compatible. Code leaves login/refresh/logout request and response construction unchanged; `docs/working/API_CONTRACTS.md` did not need changes.
- Slice requirement: refresh rotation/replay/logout unchanged. Code leaves `UserSession.refresh_token_hash`, `issue_refresh_token()`, `active_session_for_refresh()`, `refresh()`, and `logout()` flow intact except token decode and constant-time hash comparison library.

## Tests and Evidence
- RED: `.ralph/runs/2026-07-03_075227_normal_run/evidence/terminal-logs/tdd-red-secret-key-env.log` fails against hardcoded secret.
- Focused auth run: `.ralph/runs/2026-07-03_075227_normal_run/evidence/terminal-logs/tdd-green-auth-pyjwt-focused.log` stops at missing `jwt` module before tests execute.
- Backend check/test/migration/coverage logs saved in the run folder; all stop at missing `jwt` except coverage also reports low coverage because tests cannot run.
- Frontend test/typecheck/build logs saved in the run folder; all stop at missing local frontend binaries.
- Static checks: `diff-check-results.md` clean; `hmac-grep-results.md` empty.

## Files to Review
- `sfpcl_credit/identity/views.py`
- `sfpcl_credit/config/settings.py`
- `sfpcl_credit/tests/test_auth_api.py`
- `sfpcl_credit/requirements.txt`
- `docs/slices/002C-role-and-permission-catalogue-seed.md`
- `docs/slices/002D-current-user-api-with-permissions-and-teams.md`

## Recommended Next Action
Install pinned backend/frontend dependencies in the orchestrator validation environment and rerun the gates. If PyJWT is installed, the next slice is 002C role and permission catalogue seed.
