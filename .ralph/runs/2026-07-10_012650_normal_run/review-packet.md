# Review Packet

## Slice
005G2-member-portal-session-and-audit-contract-hardening

## Traceability
- Source says inactive/suspended portal users are blocked (`screen-spec-member-portal.md` MP00 and
  §14.1, distilled in `docs/working/digests/epic-005-application-intake.md`). Code now rejects and
  revokes active sessions when the linked `PortalAccount` is not active. Verified by:
  `test_suspended_portal_account_invalidates_existing_session_for_current_user`,
  `test_suspended_portal_account_cannot_change_password_with_existing_session`, and
  `test_suspended_portal_account_cannot_use_existing_session_for_portal_routes`.
- Source names portal audit actions `portal.login.success`, `portal.login.failed`,
  `portal.account.activated`, `portal.application.draft_created`, `portal.application.saved`,
  `portal.application.submitted`, and `portal.password.changed`. Code writes those names only for
  portal routes. Verified by `test_valid_invited_member_can_activate_and_login_with_member_scoped_tokens`,
  `test_failed_portal_login_audits_source_event_without_sensitive_values`,
  `test_security_settings_password_change_audits_and_revokes_other_sessions`, and
  `test_portal_borrower_can_create_update_submit_list_and_read_own_application_status`.
- Staff application routes must preserve internal audit actions. Code adds defaulted audit-action
  override parameters and only portal services pass portal names. Verified by the full staff loan
  application API tests, including staff create/update/submit audit assertions.
- Audit payloads must remain metadata-only. Tests assert portal auth/application audit payloads do
  not contain passwords, OTPs, PAN, Aadhaar, or sensitive raw values.

## Evidence
- Red: `evidence/terminal-logs/red-portal-suspended-auth-me.log`
- Red: `evidence/terminal-logs/red-portal-auth-audit-actions.log`
- Red: `evidence/terminal-logs/red-portal-application-audit-actions.log`
- Green focused: `evidence/terminal-logs/green-focused-backend-portal-and-applications.log`
- Backend gates: `backend-check.log`, `backend-tests.log`, `backend-makemigrations-check.log`,
  `backend-coverage.log`
- Frontend gates: `frontend-lint.log`, `frontend-typecheck.log`, `frontend-tests.log`,
  `frontend-build.log`

## Gate Summary
- Backend check: passed.
- Backend tests: 269 passed.
- Backend migration check: passed, no changes detected.
- Backend coverage: 95%, above the 85% floor.
- Frontend lint: passed.
- Frontend typecheck: passed.
- Frontend tests: 90 passed.
- Frontend build: passed.

## Reviewer Notes
- No database migration was needed.
- No frontend implementation changed.
- A-044 records that suspended old portal sessions return `401 INVALID_TOKEN` on portal routes
  because the shared bearer-session validator runs before route-level portal permission logic.
