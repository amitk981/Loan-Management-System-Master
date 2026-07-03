# Execution Plan

Selected slice: 002B2-auth-hardening-jwt-library-and-packaging

## Scope
- Replace the custom HMAC JWT implementation in `sfpcl_credit/identity/views.py` with PyJWT HS256 encode/decode.
- Preserve the implemented auth API response/request fields and error envelope for login, refresh, and logout.
- Move `SECRET_KEY` configuration to `SFPCL_SECRET_KEY` with the current local development value as fallback.
- Pin PyJWT in `sfpcl_credit/requirements.txt`; do not run network installs.

## Constraints Checked
- Writable by permissions: `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`, `.ralph/runs/**`, `.ralph/progress.md`, `.ralph/state.json`.
- Protected/read-only: `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/source/**`, `docs/working/DECISION_POLICY.md`, `docs/working/FRONTEND_DESIGN_RULES.md`, `docs/working/HIGH_RISK_APPROVALS.md`.
- Backend commands must use `/Users/amitkallapa/Loan Management System Development/.ralph/venv/bin/python`.

## TDD Plan
1. Add one public-interface auth test proving a refresh token signed with a wrong secret is rejected with the existing `401` error envelope; run it and save red evidence.
2. Implement the minimal PyJWT decode path and secret configuration needed for that behavior; run the focused auth tests and save green evidence.
3. Add one public-interface auth test proving an expired access token is rejected by the shared token decoder; run it and save red evidence if it is not already covered by the PyJWT implementation.
4. Complete cleanup: remove hand-rolled base64/HMAC helpers, keep SHA-256 refresh-token storage hashing and constant-time hash comparison behavior through `secrets.compare_digest`.
5. Run required backend and frontend quality gates, plus acceptance checks for no `hmac` import/usage in `sfpcl_credit/identity/`.

## Evidence To Save
- Red/green terminal logs in `.ralph/runs/2026-07-03_080407_normal_run/evidence/terminal-logs/`.
- Final gate logs for backend check, backend tests, migrations check, coverage, frontend test/typecheck/build.
- `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.
