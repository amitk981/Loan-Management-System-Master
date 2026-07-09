# Ralph Handoff

## Last Run
2026-07-10_005716_architecture_review

## Current Status
Architecture review completed for the four slices merged since prior architecture-review commit
`49da479`:
- `005F2-deficiency-return-status-contract-hardening`
- `005FA-member-portal-authentication`
- `005FB-member-portal-dashboard-profile-and-supply-view`
- `005G-member-portal-application-start-status`

Findings:
- High: suspended portal accounts are blocked at fresh login and portal data routes, but existing
  sessions can still expose portal claims through `/auth/me` because the shared current-user/token
  payload paths check only `UserSession` and `User.status`, not `PortalAccount.status`.
- Medium: portal audit rows are metadata-only, but their action names diverge from the source portal
  audit table. Current code uses names such as `portal.auth.login.succeeded` and internal
  `applications.loan_application.*` for borrower portal draft/submit instead of
  `portal.login.success`, `portal.account.activated`, `portal.application.draft_created`,
  `portal.application.saved`, and `portal.application.submitted`.
- Pass: portal own-data boundaries are otherwise carried through 005FB/005G by deriving authority
  from active `PortalAccount.member_id`, not client-supplied member IDs.
- Pass: reviewed tests have substantive red/green coverage and full gates passed in the reviewed
  runs.

Source facts used:
- `screen-spec-member-portal.md` MP00 says inactive/suspended portal users are blocked.
- `screen-spec-member-portal.md` §14.1 says inactive or unauthorised portal accounts are blocked.
- `screen-spec-member-portal.md` §11 names source portal audit events.
- `functional-spec.md` M03 requirements confirm borrower portal initiation/save/submit and the
  existing completeness/deficiency/reference sequencing.

## Validation
- Backend `manage.py check` passed.
- Backend tests passed: 265 tests.
- Backend coverage passed: 95%, above 85% floor.
- Backend `makemigrations --check --dry-run` passed.
- Frontend lint, typecheck, tests, and build passed.
- `git diff --check` and protected-path scan passed.

Evidence is in `.ralph/runs/2026-07-10_005716_architecture_review/`.

## Next Run
Run `005G2-member-portal-session-and-audit-contract-hardening`.

Key instructions for 005G2:
- TDD first: add failing tests for an already-issued portal token after
  `PortalAccount.status = suspended`; `/auth/me`, password change, portal dashboard/profile/supply,
  and portal application endpoints must no longer expose portal authority.
- Centralise portal-session validity so login, current-user payloads, password change, and portal
  own-data helpers agree on active account status. Prefer revoking active sessions with
  `portal_account_status_changed` or an equally explicit reason.
- Align portal audit action names with the source table while preserving existing internal staff
  `applications.*` audit actions for staff routes.
- Keep audit payloads metadata-only and prove no sensitive values, OTPs, token hashes, or raw
  document contents are recorded.
- After 005G2 passes, continue with `005H-rejection-note-shell`.

Key instructions for 005H:
- 005H now depends on 005G2.
- Keep rejection-note work staff-only. Borrower portal tokens must not create/send rejection notes.
- Reuse staff application object-access boundaries from 005C2 and later slices.
- Rejection-note create/send must not generate `LO...` references, register rows, sequence values,
  or appraisal/sanction/disbursement state.
- Preserve `incomplete_returned` as distinct borrower rectification work; do not use rejection
  notes to repeat-return deficiencies.
- Update API contracts and add metadata-only audit/workflow tests.
