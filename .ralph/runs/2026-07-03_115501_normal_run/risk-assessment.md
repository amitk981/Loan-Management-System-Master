# Risk Assessment — 002C2 Standard API Envelope and Auth Service Boundary

## Declared risk level
High (auth-touching refactor). Standing approval applies (`docs/working/HIGH_RISK_APPROVALS.md`, not revoked). No new endpoint, no model/migration change, no new dependency, no frontend change.

## What changed
- New `sfpcl_credit/api.py`: the single production response-envelope implementation (`success_response`, `error_response`, `response_meta`) plus request helpers (`parse_json_body`, `request_ip`, `request_user_agent`).
- New `sfpcl_credit/identity/modules/tokens.py` and `auth_service.py`: token/session/audit behavior moved behind an explicit module interface.
- `sfpcl_credit/ops.py` and `sfpcl_credit/identity/views.py` rewritten to import the shared helper and delegate to the module; views are now thin. `views.py` re-exports `TokenError`/`decode_token` for backward-compatible imports.

## Why this is honest about risk
This slice touches the authentication path — the highest-value security surface in the product. The mitigating facts:
- **Behavior preserved, proven by unchanged tests.** The existing `sfpcl_credit/tests/test_auth_api.py` (login, invalid/inactive credentials, refresh rotation + replay rejection, wrong-secret rejection, expired-access rejection, logout revocation, env-secret loading) was **not modified** and passes against the refactored code. That is the strongest evidence that PyJWT HS256, lifetimes, claims, rotation, replay rejection, logout revocation, inactive-user rejection, and audit events are unchanged.
- New module-level tests (`test_auth_module.py`) exercise the same behaviors directly through the module interface.
- New envelope tests (`test_api_envelope.py`) prove health + auth share identical `meta` keys and that both endpoints delegate to the one shared helper (identity assertion), so the envelope cannot silently drift again.

## Deliberate behavior change
- Health responses now include `meta.api_version: "v1"` (previously absent). This is the only intended contract change and is required by the slice and `docs/source/api-contracts.md` §6.1. No status codes, URLs, or `data` fields changed.

## Residual risks / open items
- **A-008 (Medium):** `auth_service.validate_access_token` is stateless (signature/expiry/type only, no session-active check) — preserves existing 002B behavior. 002D's `/auth/me/` must decide whether to bind access-token validation to an active session. Recorded in `ASSUMPTIONS.md` and the 002D slice.
- Uncovered lines are error-path branches in the thin views (malformed body / missing-field responses) already present before this slice; overall backend coverage 96% vs 85% floor.

## Reversibility
Fully reversible: no schema/data/dependency change. Reverting the file set restores prior behavior exactly.

## Gate results
Backend `check` clean; `makemigrations --check` = "No changes detected"; full suite 33/33; coverage 96%. Frontend typecheck + 5 tests + build all green. Protected files untouched. Diff: 8 tracked files + 6 new files, +92/-252 tracked lines — within limits (30 files / 2000 lines / 4 deps / 1 migration).
