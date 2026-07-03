# Execution Plan

Selected slice: 002B2-auth-hardening-jwt-library-and-packaging

## Scope
- Replace hand-rolled JWT signing/verification in `sfpcl_credit/identity/views.py` with PyJWT HS256 encode/decode.
- Preserve the implemented auth API contracts for login, refresh, and logout.
- Move the Django `SECRET_KEY` source to `SFPCL_SECRET_KEY` with the existing local development value as fallback.
- Add pinned `PyJWT` to `sfpcl_credit/requirements.txt`.

## Permission Check
- Allowed to edit: `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`, `.ralph/runs/**`, `.ralph/progress.md`, `.ralph/state.json`.
- Protected or forbidden paths will not be edited: `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/working/HIGH_RISK_APPROVALS.md`, `docs/working/DECISION_POLICY.md`, `docs/working/FRONTEND_DESIGN_RULES.md`, `docs/source/**`.

## TDD Plan
1. RED: Add a public-endpoint test proving refresh rejects a token signed with the wrong secret.
2. RED: Add a public-endpoint test proving refresh rejects an expired token.
3. GREEN: Replace custom JWT helpers with PyJWT while keeping error codes and response envelopes stable.
4. GREEN: Update settings and requirements for environment-backed secret and pinned dependency.

## Verification
- Save red/green auth test output under `.ralph/runs/2026-07-03_065754_normal_run/evidence/terminal-logs/`.
- Run backend checks, tests, migration sync, and coverage.
- Run frontend typecheck, tests, and build because Ralph gates require them.
- Verify no `hmac` usage remains under `sfpcl_credit/identity/`.
- Confirm `docs/working/API_CONTRACTS.md` still describes unchanged auth request/response fields.
