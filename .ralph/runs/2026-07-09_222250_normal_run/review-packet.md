# Review Packet

Run: 2026-07-09_222250_normal_run  
Slice: 005FA-member-portal-authentication

## Implementation Summary
- Added `PortalAccount` and `PortalOtpChallenge` identity models plus migration `0003_portal_member_auth`.
- Added portal auth service and endpoints for account activation, portal login, password reset, and password change.
- Extended access token claims and `/api/v1/auth/me/` with borrower portal scope:
  `member_id`, `portal_account_id`, and `portal_role = borrower_member`.
- Wired MP00, MP01, MP02, and MP25 to the real backend APIs while keeping existing visual classes and layout patterns.
- Updated API contracts, assumptions, Epic 005 digest, handoff, progress, and sharpened 005FB/005G.

## Traceability
- Source says MP01 activation verifies member identity/contact and OTP before setting a password
  (`screen-spec-member-portal.md` MP01). Code does this through
  `portal_activation_start` and `portal_activation_complete`, verified by
  `test_valid_invited_member_can_activate_and_login_with_member_scoped_tokens`.
- Source says borrower/member portal users access only their own records
  (`auth-permissions.md` §4.2, §14, and borrower object-denial examples). Code adds member-scoped
  token claims and portal own-data permissions only; the backend test proves the borrower token is
  denied on a staff deficiency-return endpoint.
- Source says invalid credential/reset flows must not reveal whether an account exists
  (`screen-spec-member-portal.md` MP00/MP02 and `security-privacy.md` §10). Code returns generic
  invalid credential and reset-start responses.
- Source says password reset revokes sessions (`screen-spec-member-portal.md` MP02 and
  `security-privacy.md` SEC-AUTH-004). Code revokes active sessions with
  `portal_password_reset`, verified by
  `test_password_reset_is_single_use_and_revokes_existing_sessions`.
- Source says profile security changes are audited (`screen-spec-member-portal.md` MP25). Code
  writes `portal.auth.password_changed`, verified by
  `test_security_settings_password_change_audits_and_revokes_other_sessions`.

## Evidence
- Backend RED: `evidence/terminal-logs/backend-portal-auth-red.log`
- Backend GREEN: `evidence/terminal-logs/backend-portal-auth-green-attempt-3.log`
- Frontend RED: `evidence/terminal-logs/frontend-auth-session-red.log`
- Frontend GREEN: `evidence/terminal-logs/frontend-auth-session-green.log`
- Full backend tests: `evidence/terminal-logs/backend-tests-full.log`
- Backend coverage: `evidence/terminal-logs/backend-coverage.log`
- Frontend gates: `frontend-lint.log`, `frontend-typecheck-final.log`,
  `frontend-tests-full.log`, `frontend-build.log`
- Visual evidence: `evidence/portal-auth-visual-evidence.html`
- Visual render limitation logs: `visual-evidence-render.log`; Playwright/Vite failure details
  are in terminal history for this run.

## Known Limitations
- Real SMS/email provider delivery is not implemented; OTP challenge creation writes a
  communication-shell row only. A-042 owns this assumption.
- PAN/Aadhaar last-four verification uses current placeholder stored values until a sensitive-value
  adapter exists. A-042 owns this assumption.
- Browser screenshots could not be captured due sandbox browser/server restrictions; self-contained
  visual HTML evidence is saved instead.

## Gates
- Backend `manage.py check`: passed.
- Backend full tests: 260/260 passed.
- Backend migrations check: passed.
- Backend coverage: 95%, above 85% floor.
- Frontend lint: passed.
- Frontend typecheck: passed.
- Frontend tests: 83/83 passed.
- Frontend build: passed.
- `git diff --check`: passed.
- Protected-path scan: passed.
