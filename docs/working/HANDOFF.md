# Ralph Handoff

## Last Run
2026-07-09_222250_normal_run

## Current Status
Slice `005FA-member-portal-authentication` completed successfully.

What changed:
- Added portal auth models: `PortalAccount` links one `Member` to one borrower portal `User`;
  `PortalOtpChallenge` stores activation/reset OTP hashes, status, expiry, and challenge metadata.
- Added portal endpoints:
  `/api/v1/portal/auth/activation/start/`,
  `/api/v1/portal/auth/activation/complete/`,
  `/api/v1/portal/auth/login/`,
  `/api/v1/portal/auth/password-reset/start/`,
  `/api/v1/portal/auth/password-reset/complete/`, and
  `/api/v1/portal/auth/password/change/`.
- Borrower access tokens and `/api/v1/auth/me/` now include `member_id`, `portal_account_id`, and
  `portal_role = borrower_member`. They expose only portal own-data permission codes and do not
  grant staff completeness, reference generation, return-with-deficiencies, or deficiency
  resolution authority.
- Password reset OTPs are single-use and revoke active sessions; MP25 password change revokes
  other sessions while keeping the current session active.
- MP00/MP01/MP02/MP25 now call real APIs while preserving existing visual patterns.
- API contracts, A-042, the Epic 005 digest, and next portal slices were updated with the member
  scope and OTP-delivery assumptions.

Source facts used:
- `docs/source/screen-spec-member-portal.md` MP00/MP01/MP02/MP25 require login, activation,
  OTP/password reset, and security settings.
- `docs/source/auth-permissions.md` §5 requires JWT session tracking, minimal claims, refresh
  revocation, and no sensitive token data; borrower portal users are own-record users.
- `docs/source/security-privacy.md` requires generic invalid-credential/reset handling, OTP/hash
  protections, failed-login auditability, and session revocation on password reset.
- `docs/source/api-contracts.md` §11 defines auth envelope conventions.

## Validation
- TDD red/green saved for backend portal auth and frontend auth-session API wiring.
- Focused portal auth backend module passed: 4 tests.
- Full backend suite passed: 260 tests.
- Backend coverage passed: 95% total, above 85% floor.
- Backend `manage.py check` and `makemigrations --check --dry-run` passed.
- Frontend lint, typecheck, tests (83/83), and build passed.
- `git diff --check` passed.
- Visual evidence HTML is saved. Browser screenshots could not be captured in this sandbox because
  Vite server binding failed with `EPERM`, in-app browser was unavailable, and Playwright Chromium
  launch failed with macOS Mach port permission denial; logs are in the run folder.

Evidence is in `.ralph/runs/2026-07-09_222250_normal_run/`.

## Next Run
Run `005FB-member-portal-dashboard-profile-and-supply-view`.

Key instructions for 005FB:
- Consume `member_id` and `portal_role = borrower_member` from the authenticated portal token and
  `/auth/me`; do not accept arbitrary member IDs from the client as authority.
- Borrower portal reads should use portal own-data permissions, not staff `members.member.read` or
  `applications.loan_application.*` grants.
- Preserve masking for PAN/Aadhaar/full bank values; no portal reveal path exists yet.
- Dashboard pending actions may count open deficiencies for the member's own applications, but
  application list/status screens belong to 005G.
