# Review Packet: 2026-07-03_115501_normal_run

## Result
Success

## Slice
002C2-standard-api-envelope-and-auth-service-boundary (High risk; standing approval, not revoked)

## What this slice did, in plain English
An earlier independent architecture review (2026-07-03_081509) flagged two problems in the
freshly-built auth code, before the next auth endpoint gets added:
1. The "response envelope" (the standard shape every API reply uses) was **copy-pasted** in two
   places — one for health checks, one for login/logout — and they had already started to disagree
   (the health copy was missing the `api_version` field). Two copies drift; the contract breaks quietly.
2. The login/logout view functions were doing too much: signing tokens, looking up sessions, rotating
   refresh tokens, revoking on logout, and writing audit logs all inline. The architecture guidance
   says the web-facing view should be thin and hand that work to named, testable functions.

This slice fixes both without changing how the API behaves:
- There is now **one** envelope helper (`sfpcl_credit/api.py`) used by both health and auth. Health
  replies now include the previously-missing `api_version: "v1"`. Nothing else about any reply changed.
- The auth work now lives behind explicit, directly-testable functions in
  `sfpcl_credit/identity/modules/` (`tokens.py`, `auth_service.py`). The views just read the request,
  call those functions, and turn known errors into standard error replies.

## Traceability (source says X → code does X → test proves it)
- **Source:** `docs/source/api-contracts.md` §6.1 — success envelope `meta` must include `request_id`,
  `timestamp`, `api_version`. **Code:** `sfpcl_credit/api.py::response_meta`. **Test:**
  `test_api_envelope.py::test_all_health_endpoints_include_api_version_v1` and
  `test_health_and_auth_share_the_same_standard_meta_keys` (now includes login/refresh/logout).
- **Source:** `docs/source/technical-architecture.md` §13.1 + `codebase-design.md` §6-7 — views translate
  HTTP and call module interfaces; multi-entity ops + audit live in explicit modules exercised by tests.
  **Code:** thin `sfpcl_credit/identity/views.py` delegating to `identity/modules/auth_service.py`.
  **Test:** `test_auth_module.py` drives `authenticate_user`, `issue_login_tokens_and_session`,
  `validate_refresh_session`, `rotate_refresh_token`, `revoke_session_for_logout`,
  `validate_access_token`, `record_auth_event` directly.
- **Source (preservation):** `docs/source/auth-permissions.md` §5-6 auth behavior. **Code:** logic moved,
  not changed. **Test:** the **unmodified** `test_auth_api.py` still passes (rotation, replay rejection,
  logout revocation, inactive-user rejection, wrong-secret and expired-token rejection, env secret).

## Gates
- Backend: `manage.py check` clean, `makemigrations --check` = no changes, full suite **33/33**, coverage **96%** (floor 85%). Red→green evidence saved.
- Frontend: typecheck clean, **5/5** vitest, build ok (no frontend files touched).
- Protected files: none modified. Diff within all limits.

## Evidence
`.ralph/runs/2026-07-03_115501_normal_run/evidence/terminal-logs/`:
`backend-red.log`, `backend-green.log`, `frontend-gates.log`.

## Open item carried forward
- **A-008:** `validate_access_token` is stateless by design (kept 002B behavior). 002D's `/auth/me/`
  decides whether to bind it to an active session so logout invalidates it. Recorded in `ASSUMPTIONS.md`
  and 002D slice with concrete starting points.

## Recommended Next Action
Proceed to `002D-current-user-api-with-permissions-and-teams` (now sharpened with the exact module
functions and permission-resolution query to use).
