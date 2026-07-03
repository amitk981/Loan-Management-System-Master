# Execution Plan — 002C2 Standard API Envelope and Auth Service Boundary

Slice: `docs/slices/002C2-standard-api-envelope-and-auth-service-boundary.md`
Risk: High (standing approval, not revoked in HIGH_RISK_APPROVALS.md).
Mode: backend refactor only. No new endpoint, no model/migration change, no frontend change.

## Goal
Correct architecture-review findings 1 & 2 (2026-07-03_081509_architecture_review) before 002D:
1. One shared API envelope helper for health + auth (health gains missing `meta.api_version`).
2. Auth token/session/audit behavior moved out of thin views into explicit module functions.

Preserve all 002B/002B2 behavior: PyJWT HS256, token lifetimes, JWT claims, refresh rotation,
replay rejection, logout revocation, inactive-user rejection, and auth audit events. No URL,
status-code, or field changes except adding `meta.api_version` to health responses.

## Source fidelity
- `docs/source/api-contracts.md` §6.1 success envelope = `success`, `data`, `meta{request_id,timestamp,api_version}`; §6.4 error envelope = `success:false`, `error{code,message,details,field_errors}`, `meta`. Current auth helper already matches; health helper lacks `api_version`.
- `docs/source/technical-architecture.md` §13.1 + `codebase-design.md` §6-7: views translate HTTP and call module interfaces; multi-entity ops + audit live in explicit modules, tests exercise those interfaces.

## Design
New files:
- `sfpcl_credit/api.py` — shared HTTP envelope + request helpers:
  `response_meta`, `success_response`, `error_response`, `parse_json_body`, `request_ip`, `request_user_agent`. Single production envelope implementation.
- `sfpcl_credit/identity/modules/__init__.py`
- `sfpcl_credit/identity/modules/tokens.py` — `TokenError`, `encode_token`, `decode_token`, `hash_token`, `access_claims`, `refresh_claims`.
- `sfpcl_credit/identity/modules/auth_service.py` — explicit auth module interface:
  - `authenticate_user(email, password)` -> user | raises `CredentialError(outcome, user)`
  - `issue_login_tokens_and_session(user, request)` -> `(session, payload)` (create session, issue refresh, set last_login, build payload)
  - `validate_refresh_session(refresh_token)` -> session (decode + session lookup + active + hash match + user-active; raises `TokenError`)
  - `rotate_refresh_token(session)` -> new refresh_token (hash-store + last_used)
  - `revoke_session_for_logout(session)` -> revokes with reason `logout`
  - `validate_access_token(access_token)` -> claims (decode access token for future callers / 002D; stateless — matches existing access-token design)
  - `record_auth_event(request, action, ...)` -> AuditLog row
  - `auth_payload(user, session, refresh_token)` -> dict

Rewrite:
- `sfpcl_credit/ops.py` — import `success_response` from `sfpcl_credit.api`; keep health handlers; responses now carry `meta.api_version`.
- `sfpcl_credit/identity/views.py` — thin `login`/`refresh`/`logout` that parse input, call `auth_service`, translate `CredentialError`/`ValidationError`/`TokenError` to standard responses. Re-export `TokenError` and `decode_token` for backward-compatible imports (`tests/test_auth_api.py`).
- `sfpcl_credit/config/urls.py` — unchanged (imports stay valid).

## TDD steps (red -> green, evidence saved to evidence/terminal-logs/)
1. RED: `tests/test_api_envelope.py` — health live/ready/deep include `meta.api_version == "v1"`; login/refresh/logout/health all expose identical meta key set `{request_id,timestamp,api_version}`. Fails today (health lacks api_version).
2. RED: `tests/test_auth_module.py` — module-interface tests: `authenticate_user` success/invalid/inactive; `issue_login_tokens_and_session` creates active session + payload; `validate_refresh_session` + `rotate_refresh_token` rotation & replay rejection; `revoke_session_for_logout` blocks reuse; `validate_access_token` decodes valid / rejects expired & wrong-type; `record_auth_event` writes audit. Fails today (module absent).
3. GREEN: add `api.py`, `modules/`, rewrite `ops.py` and `views.py`. Re-run both new suites + existing `test_auth_api.py` + `test_health_api.py` + catalogue tests.
4. Full backend gates: `manage.py check`, full test suite, `makemigrations --check` (expect no migration), coverage >= 85%.
5. Frontend gates unchanged: `npm run build`, `npm run typecheck`, `npm test` (no frontend files touched).

## Artifacts
changed-files.txt, risk-assessment.md, review-packet.md, red/green + gate logs under evidence/terminal-logs/, updated API_CONTRACTS.md (health envelope shows api_version + shared helper note), HANDOFF/state/progress/slice status, ASSUMPTIONS if any judgment call.

## Assumptions to record
- `validate_access_token` is stateless (decode only), consistent with existing access-token design where logout revokes the refresh session but short-lived access tokens remain valid until expiry (002B behavior, unchanged). Session-bound access checks, if wanted, are a 002D decision.
