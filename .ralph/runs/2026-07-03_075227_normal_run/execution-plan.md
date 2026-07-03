# Execution Plan

Selected slice: 002B2-auth-hardening-jwt-library-and-packaging

## Scope
- Backend only: `sfpcl_credit/identity/views.py`, `sfpcl_credit/config/settings.py`, `sfpcl_credit/requirements.txt`, and auth tests.
- Keep auth API request/response/error contracts unchanged.
- Do not change refresh-session rotation, replay rejection, logout revocation, frontend code, source docs, scripts, or protected files.

## Permission Check
- Allowed paths: `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`, `.ralph/runs/**`, `.ralph/state.json`, `.ralph/progress.md`.
- Forbidden/protected paths will not be edited: `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/source/**`, `docs/working/HIGH_RISK_APPROVALS.md`, `docs/working/DECISION_POLICY.md`, `docs/working/FRONTEND_DESIGN_RULES.md`.

## TDD Plan
1. Inspect current auth tests and token implementation.
2. Add one regression test proving a wrong-secret signed token is rejected; run the focused test and save RED evidence.
3. Replace hand-rolled HMAC token handling with PyJWT, pin `PyJWT` in requirements, and make `SECRET_KEY` read from `SFPCL_SECRET_KEY` with current fallback.
4. Run the focused test and save GREEN evidence.
5. Add/run the expired access-token regression if not already covered by the public API tests; keep behavior verified through public auth endpoints/helpers used by the API.
6. Run required backend and frontend gates, saving outputs under `.ralph/runs/2026-07-03_075227_normal_run/`.

## Completion Artifacts
- `changed-files.txt`
- `risk-assessment.md`
- `review-packet.md`
- `final-summary.md`
- Updated `docs/working/HANDOFF.md`, `.ralph/state.json`, `.ralph/progress.md`, and slice status.
- Sharpen the next 1-2 Not Started slices using already-opened epic/digest context.
