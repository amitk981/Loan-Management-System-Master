# Ralph Handoff

## Last Run
2026-07-10_015723_normal_run

## Current Status
Completed `005H-rejection-note-shell`.

What changed:
- Added the staff-only rejection-note metadata shell:
  `POST /api/v1/loan-applications/{loan_application_id}/rejection-note/` and
  `POST /api/v1/rejection-notes/{rejection_note_id}/send/`.
- Added `rejection_notes` persistence with one non-destructive migration. The shell stores source
  metadata only: stage, reason category, detailed reason, reapply flag, communication mode,
  prepared actor, optional approval/communication facts, `note_status = draft/sent`, and sent actor
  timestamps.
- Reused `applications.loan_application.complete_check` plus existing loan-application object access
  because no narrower source-backed rejection-note permission exists yet.
- Active borrower portal tokens receive `403 PERMISSION_DENIED` on staff rejection-note routes.
  Old sessions for suspended portal accounts receive `401 INVALID_TOKEN` before any side effect.
- Create is limited to submitted applications with no `LO...` reference, no loan request register
  row, and no existing rejection note. Invalid state, duplicate create, duplicate send, permission
  denial, object denial, and validation failures create no rejection-note success audit/workflow
  side effects.
- Successful create writes `applications.rejection_note.created` and a `rejection_note` workflow
  event into `draft`. Successful send writes `applications.rejection_note.sent`, stamps
  `sent_by_user`/`sent_at`, and records `draft -> sent`.
- Send is metadata-only in this slice. It validates `recipient_email` but does not create a
  `communications` row, call a provider, generate a PDF, or expose borrower portal delivery.
- A-045 records that `LoanApplication.application_status` remains `submitted` because the current
  intake status vocabulary has no source-backed generic rejected state.

## Validation
- TDD red evidence saved for missing rejection-note create route (`404 != 200`).
- Focused rejection-note tests passed: 3 tests.
- Focused loan-application API tests passed: 21 tests.
- Backend `manage.py check` passed.
- Backend tests passed: 272 tests.
- Backend `makemigrations --check --dry-run` passed.
- Backend coverage passed: 95%, above 85% floor.
- Frontend lint, typecheck, tests, and build passed.
- `git diff --check` passed.

Evidence is in `.ralph/runs/2026-07-10_015723_normal_run/`.

## Next Run
Run `005I-application-intake-frontend-wiring`.

Key instructions for 005I:
- Staff screens must use staff `/api/v1/loan-applications/` APIs, not portal routes.
- Do not reintroduce `mockData.ts` application rows into wired staff Application List, New
  Application, or Application Detail.
- Preserve submitted applications with no `LO...` reference until completeness pass.
- Display `incomplete_returned` distinctly as borrower rectification work.
- If rejection-note metadata is shown, keep it separate from `application_status`; do not invent a
  frontend-only rejected application state.
- Rejection-note controls, if surfaced through existing action slots, are staff-only and must reuse
  existing visual patterns without new styling.
