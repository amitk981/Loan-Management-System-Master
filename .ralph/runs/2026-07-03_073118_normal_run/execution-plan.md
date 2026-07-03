# Execution Plan

Selected slice: 002B2-auth-hardening-jwt-library-and-packaging

## Scope
- Replace hand-rolled JWT signing/verification in `sfpcl_credit/identity/views.py` with pinned `PyJWT`.
- Keep the existing login, refresh, and logout API request/response contracts unchanged.
- Move Django `SECRET_KEY` to `SFPCL_SECRET_KEY` with the current local development value as fallback.
- Preserve refresh-session storage, token rotation, replay rejection, logout revocation, and auth audit behavior.

## Permission Check
- Allowed edits: `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`, `.ralph/runs/**`.
- Forbidden/protected paths will not be edited: `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/source/**`, risk/policy files.

## TDD Plan
1. Add one public-API test proving a refresh token signed with the wrong secret is rejected.
2. Run that test and save RED output to `evidence/terminal-logs/`.
3. Implement PyJWT encode/decode and dependency/settings changes.
4. Run the new test and existing auth tests, saving GREEN output.
5. Add/verify the expired access-token behavior through the public decode path and save evidence.

## Validation Plan
- Verify no hand-rolled HMAC signing remains under `sfpcl_credit/identity/`.
- Run backend gates: `manage.py check`, tests, migration check, coverage.
- Run frontend gates required by Ralph: `npm run typecheck`, `npm test`, `npm run build`.
- Save changed files, risk assessment, review packet, final summary, and gate logs.
- Update handoff, progress, state, and slice status after gates pass.
