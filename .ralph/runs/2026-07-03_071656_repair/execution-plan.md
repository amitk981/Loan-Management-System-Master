# Execution Plan

Run ID: 2026-07-03_071656_repair
Slice: 002B2-auth-hardening-jwt-library-and-packaging
Mode: repair

## Repair Diagnosis
- Newest prior FAIL artifact: `.ralph/runs/2026-07-02_152218_normal_run/preflight-results.md` failed on an active Ralph lock; current repair preflight reports no active locks.
- Leftover worktree inspected read-only: `/Users/amitkallapa/Loan Management System Development/.ralph/worktrees/2026-07-03_065754_normal_run`.
- Leftover worktree contained ungated changes for this slice. Its saved gate files show dependency/tooling failures: missing Rollup optional native package for frontend build/tests and missing Python `coverage`; commit also failed there because the sandbox could not create a git index lock.
- Current repair worktree starts clean except for current run artifacts. It also lacks installed `jwt`, `coverage`, and Rollup native optional dependency, so dependency installation/gate behavior must be captured honestly.

## Permissions Check
- Allowed paths for this slice: `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`, `.ralph/progress.md`, `.ralph/state.json`, `.ralph/runs/**`.
- Protected/forbidden paths will not be edited: `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/working/HIGH_RISK_APPROVALS.md`, `docs/working/DECISION_POLICY.md`, `docs/working/FRONTEND_DESIGN_RULES.md`, `docs/source/**`.

## Plan
1. Add focused failing auth tests first:
   - Wrong-secret refresh token is rejected.
   - Expired access token is rejected through the token decoder seam.
2. Save red evidence under `.ralph/runs/2026-07-03_071656_repair/evidence/terminal-logs/`.
3. Add pinned `PyJWT` to `sfpcl_credit/requirements.txt` and install/verify import if the local environment permits it.
4. Replace custom JWT base64/HMAC encode/decode helpers in `sfpcl_credit/identity/views.py` with PyJWT HS256 encode/decode while preserving existing claims, lifetimes, response envelopes, and refresh-session behavior.
5. Move `SECRET_KEY` to `SFPCL_SECRET_KEY` with the existing local development fallback.
6. Run focused auth tests, full backend tests/check/migrations/coverage, frontend typecheck/tests/build, and the no-HMAC scan; save outputs.
7. Update required Ralph artifacts: changed files, risk assessment, review packet, final summary, state/progress/handoff/slice status, and sharpen the next 1-2 Not Started slices using already-opened Epic 002/digest context.
8. Commit only if gates pass and the sandbox permits git writes.
