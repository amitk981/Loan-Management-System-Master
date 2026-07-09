# Ralph Handoff

## Last Run
2026-07-10_012650_normal_run

## Current Status
Completed `005G2-member-portal-session-and-audit-contract-hardening`.

What changed:
- Added a shared portal-session authority check in the auth boundary. If a linked
  `PortalAccount` is not active or its member is deleted, active access/refresh sessions are
  revoked with `revoked_reason = portal_account_status_changed` and rejected as
  `401 INVALID_TOKEN`.
- `/api/v1/auth/me/`, portal password change, portal dashboard/profile/produce-supply, and portal
  application endpoints no longer expose portal `member_id`, `portal_account_id`, `portal_role`, or
  portal own-data permissions after portal account suspension.
- Portal audit actions now match the member-portal source table:
  `portal.account.activated`, `portal.login.success`, `portal.login.failed`,
  `portal.password.changed`, `portal.application.draft_created`,
  `portal.application.saved`, and `portal.application.submitted`.
- Staff application routes continue to write internal `applications.loan_application.created`,
  `applications.loan_application.updated`, and `applications.loan_application.submitted` audit
  actions. Portal-specific names are passed only by borrower portal services.
- API contracts, Epic 005 digest, A-044, and next slices `005H`/`005I` were updated with these
  facts.

## Validation
- TDD red logs saved for suspended `/auth/me`, portal auth audit names, and portal application audit
  names.
- Focused backend portal/application tests passed: 31 tests.
- Backend `manage.py check` passed.
- Backend tests passed: 269 tests.
- Backend `makemigrations --check --dry-run` passed.
- Backend coverage passed: 95%, above 85% floor.
- Frontend lint, typecheck, tests, and build passed.
- `git diff --check` passed.

Evidence is in `.ralph/runs/2026-07-10_012650_normal_run/`.

## Next Run
Run `005H-rejection-note-shell`.

Key instructions for 005H:
- Keep rejection-note work staff-only. Borrower portal tokens must not create/send rejection notes.
- For old suspended portal sessions, assert `401 INVALID_TOKEN` and no rejection-note side effects.
  For valid active portal sessions, assert `403 PERMISSION_DENIED` on staff rejection-note actions.
- Reuse staff application object-access boundaries from 005C2 and later slices.
- Rejection-note create/send must not generate `LO...` references, register rows, sequence values,
  or appraisal/sanction/disbursement state.
- Preserve `incomplete_returned` as distinct borrower rectification work; do not use rejection
  notes to repeat-return deficiencies.
- Keep staff rejection-note audit actions staff-scoped and metadata-only; do not reuse
  `portal.application.*` action names for internal staff work.
- Update API contracts and add metadata-only audit/workflow tests.
