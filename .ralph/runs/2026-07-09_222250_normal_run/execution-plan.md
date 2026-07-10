# Execution Plan

Selected slice: 005FA-member-portal-authentication

## Source-backed scope
- Implement member portal authentication for MP00, MP01, MP02, and MP25.
- Source facts:
  - `screen-spec-member-portal.md` MP00/MP01/MP02/MP25 require login, activation with member/contact/OTP verification, forgot-password OTP reset, and security settings.
  - `auth-permissions.md` §5 requires JWT access/refresh tokens, refresh revocation, minimal claims, and session IDs; §14 and §37 require borrower access to own records only and denial for another borrower’s loan.
  - `security-privacy.md` §10 requires generic login/reset errors, password hashing, session metadata, suspended/inactive blocks, single-use reset tokens, and session revocation after reset.
  - `api-contracts.md` §11 defines standard auth envelopes.

## Permission check
- Editable paths are allowed by `.ralph/permissions.json`: `sfpcl_credit/**`, `sfpcl-lms/src/**`, `docs/working/**`, `docs/slices/**`, and `.ralph/runs/**`.
- Protected/forbidden paths will not be edited: `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/source/**`, and guardrail docs.

## TDD plan
1. RED: Add backend API tests for portal activation, duplicate/unknown rejection, portal login token member scope, staff endpoint denial, reset single-use/revocation, and password change audit.
2. GREEN: Add a portal-account model, OTP/reset state, portal JWT/session helpers, HTTP endpoints, and migration.
3. RED/GREEN frontend: Add service tests for portal auth API mapping and route guard behavior where existing harness supports it.
4. GREEN frontend: Wire MP00/MP01/MP02/MP25 to real APIs while preserving existing visual classes and layout.

## Implementation notes
- Use the existing `User`/`Role`/`UserSession` JWT foundation instead of a parallel token store.
- Represent portal users as `borrower_portal_user` `User`s linked one-to-one to `Member` through a new portal account model.
- Include `member_id` and `portal_role = borrower_member` in token/current-user payloads, and grant only own-portal permissions.
- Use the existing communications adapter shell as a no-provider OTP mechanism by persisting OTP hashes server-side and recording audit metadata only.
- Record assumptions for OTP delivery channel and verification by PAN/Aadhaar last-four against encrypted test values because no real encryption/search service exists yet.

## Gates and evidence
- Save red/green command output under `.ralph/runs/2026-07-09_222250_normal_run/evidence/terminal-logs/`.
- Run focused backend tests first, then full backend check/tests/migrations/coverage and frontend lint/typecheck/tests/build.
- Save screenshots or self-contained visual evidence for MP00/MP01/MP02/MP25 states.
