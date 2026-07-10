# Review Packet: 2026-07-10_044114_normal_run

## Result
Success

## Slice
005I2-application-detail-api-state-hardening

## What Changed
- Staff application detail now serializes nullable, metadata-only `rejection_note` data when a
  `RejectionNote` exists. The summary omits `detailed_reason`, leaves `application_status`
  backend-owned, and read-only detail access writes no success audit/workflow event.
- Borrower portal application detail remains portal-safe and does not expose staff rejection-note
  metadata.
- `ApplicationDetail.tsx` no longer has the `LO00000035` special case, hardcoded witness rows, or
  hardcoded nominee PAN/Aadhaar reveal values. Missing API facts render unavailable/empty states
  with existing visual patterns.
- API contracts were updated for staff detail `rejection_note`, and 006B/006C were sharpened from
  existing Epic 006 digest facts.

## Traceability
- Source/review says: 005I2 must remove the `LO00000035` frontend-only overrides and synthetic
  witness/nominee data, and expose staff-only nullable rejection-note metadata without portal
  exposure.
- Code does: `sfpcl_credit/applications/services.py` includes `rejection_note` in staff detail
  serialization; `sfpcl-lms/src/pages/applications/ApplicationDetail.tsx` renders API-backed status,
  owner, document badge count, rejection-note summary, and unavailable states.
- Verified by: `test_staff_application_detail_returns_nullable_rejection_note_without_portal_exposure_or_read_audit`
  and `ApplicationDetail.test.tsx`.

## Evidence
- Backend red/green:
  `evidence/terminal-logs/backend-red-rejection-note-detail.log`,
  `evidence/terminal-logs/backend-green-rejection-note-detail.log`
- Frontend red/green:
  `evidence/terminal-logs/frontend-red-application-detail.log`,
  `evidence/terminal-logs/frontend-green-application-detail-expanded.log`
- Full gates:
  backend check/tests/migrations/coverage and frontend lint/typecheck/tests/build logs under
  `evidence/terminal-logs/`.
- Visual evidence:
  `evidence/application-detail-visual-evidence.html`

## Recommended Next Action
Run `006B-default-document-purpose-and-terms-eligibility-checks`.
