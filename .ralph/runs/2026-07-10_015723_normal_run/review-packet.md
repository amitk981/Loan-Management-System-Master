# Review Packet

## Summary
005H adds a backend/API rejection-note metadata shell for staff. It persists a narrow
`rejection_notes` row, supports draft creation and metadata-only send, and writes audit/workflow
evidence without advancing loan references, registers, appraisal, sanction, disbursement, or
borrower portal delivery.

## Traceability
- Source says `api-contracts.md` §21.3 creates rejection notes at
  `POST /api/v1/loan-applications/{loan_application_id}/rejection-note/` with stage, reason
  category, detailed reason, reapply flag, and communication mode. Code implements that in
  `loan_application_rejection_note` and `create_rejection_note`, verified by
  `test_rejection_note_create_and_send_records_metadata_only_staff_evidence`.
- Source says `api-contracts.md` §21.4 sends rejection notes at
  `POST /api/v1/rejection-notes/{rejection_note_id}/send/`. Code implements a metadata-only send
  stamp in `rejection_note_send` and `send_rejection_note`, verified by the same test plus duplicate
  send validation.
- Source says `data-model.md` §13.6 stores rejection-note metadata. Code adds
  `RejectionNote` and migration `0006_rejection_note.py` with application link, stage, category,
  detailed reason, reapply flag, prepared/approved/sent actors, communication mode/id, and sent
  timestamp.
- Slice says rejection-note work must not generate `LO...` references, register rows, sequence
  values, appraisal, sanction, or disbursement state. Tests assert zero register/sequence side
  effects on success and failure.
- Slice says staff-only and portal tokens denied. Tests assert active portal sessions get
  `403 PERMISSION_DENIED`, old suspended portal sessions get `401 INVALID_TOKEN`, and
  same-permission out-of-scope staff get `403 OBJECT_ACCESS_DENIED`.
- Source/slice require metadata-only audit/workflow rows. Tests assert
  `applications.rejection_note.created`, `applications.rejection_note.sent`, and `rejection_note`
  workflow events without sensitive values.

## Gates
- `manage.py check`: passed.
- Backend tests: 272 passed.
- `makemigrations --check --dry-run`: passed.
- Coverage: 95%, floor 85.
- Frontend lint/typecheck/tests/build: passed.
- `git diff --check`: passed.

## Evidence
- Red: `evidence/terminal-logs/rejection-note-red.log`.
- Green focused: `evidence/terminal-logs/rejection-note-green-1.log` and
  `evidence/terminal-logs/rejection-note-green-2.log`.
- Full gates: `evidence/terminal-logs/`.
- API examples: `api-response-examples.md`.
