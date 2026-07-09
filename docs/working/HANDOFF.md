# Ralph Handoff

## Last Run
2026-07-10_002243_normal_run

## Current Status
Slice `005G-member-portal-application-start-status` completed successfully in normal mode.

What changed:
- Added borrower portal application APIs:
  - `GET/POST /api/v1/portal/applications/`
  - `GET/PATCH /api/v1/portal/applications/{loan_application_id}/`
  - `POST /api/v1/portal/applications/{loan_application_id}/submit/`
- Portal application scope comes only from the active `PortalAccount.member_id`. Payload/query/path
  member IDs cannot broaden authority. Cross-member existing application attempts return
  `403 OBJECT_ACCESS_DENIED`; staff/non-portal tokens receive `403 PERMISSION_DENIED`.
- Draft create/update/submit reuse existing 005A/005B application services, metadata-only audit,
  and workflow behavior with the linked portal user as actor.
- Submitted portal applications can appear without an official `LO...` reference until staff
  completeness pass generates it.
- Returned-incomplete applications serialize borrower rectification state:
  `application_status = incomplete_returned`, `completeness_status = incomplete`,
  `current_stage = initial_loan_request`, `pending_with = Borrower`, open deficiency count, and
  open deficiency metadata.
- MP05 saves/submits through the portal APIs. MP09 lists real own applications and covers loading,
  empty, error, and returned-incomplete states. MP10 reads selected own application status detail.
- Staff application screens must continue to use staff `/api/v1/loan-applications/` APIs, not the
  portal routes.
- API contracts, prototype inventory/gap report, Epic 005 digest, and next slices 005H/005I were
  updated.

Source facts used:
- `screen-spec-member-portal.md` MP05/MP06/MP08 require own draft create/save/resume and submit.
- `screen-spec-member-portal.md` MP09/MP10 require own application list/status, pending owner,
  deficiency/status facts, and borrower next steps.
- `screen-spec-member-portal.md` permissions matrix marks MP05/MP09/MP10 as own-only.
- `api-contracts.md` §19 defines loan application create/read/update/submit behavior; §21 defines
  deficiency metadata.
- `data-model.md` includes `incomplete_returned` in application status and `deficiencies` linked
  to applications.

## Validation
- Backend TDD red saved: portal application endpoints initially returned `404`.
- Focused backend portal tests passed: 5 tests.
- Full backend suite passed: 265 tests.
- Backend coverage passed: 95% total, above 85% floor.
- Backend `manage.py check` and `makemigrations --check --dry-run` passed.
- Frontend portal API red/green tests passed.
- Frontend portal view tests passed, including MP09 loading/empty/error/returned-incomplete states.
- Frontend full tests passed: 90 tests.
- Frontend lint, typecheck, and build passed.
- Live screenshot capture could not run because this sandbox blocked the Vite dev server with
  `listen EPERM 127.0.0.1:5173`. The error log and static self-contained visual evidence HTML are
  saved in the run folder.

Evidence is in `.ralph/runs/2026-07-10_002243_normal_run/`.

## Next Run
Architecture review is due (`slices_completed_since_architecture_review = 4`).

After architecture review, run `005H-rejection-note-shell`.

Key instructions for 005H:
- Keep rejection-note work staff-only. Borrower portal tokens must not create/send rejection notes.
- Reuse staff application object-access boundaries from 005C2 and later slices.
- Rejection-note create/send must not generate `LO...` references, register rows, sequence values,
  or appraisal/sanction/disbursement state.
- Preserve `incomplete_returned` as distinct borrower rectification work; do not use rejection
  notes to repeat-return deficiencies.
- Update API contracts and add metadata-only audit/workflow tests.
