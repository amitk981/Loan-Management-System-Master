# Risk Assessment

## Slice
005H-rejection-note-shell

## Risk Level
Medium.

## Why
- Adds one database table and two staff mutation endpoints in the loan-origination workflow.
- Touches permission, object-access, audit, workflow, and portal-token denial behavior.
- Explicitly avoids high-risk financial state, references, registers, appraisal, sanction,
  document generation, and real communication delivery.

## Controls
- TDD red/green evidence saved under `evidence/terminal-logs/`.
- Staff routes require session-bound bearer auth, `applications.loan_application.complete_check`,
  and existing application object access.
- Borrower portal tokens are denied; suspended portal sessions fail at shared auth with
  `401 INVALID_TOKEN`.
- Invalid states and denials assert no rejection-note, audit, workflow, register, reference, or
  sequence side effects.
- One non-destructive migration only: `applications.0006_rejection_note`.
- No protected files, `docs/source/`, provider calls, or frontend styling changes were touched.

## Residual Risk
- A-045 records that the source says rejection output updates application status, but no
  source-backed generic rejected intake status exists in the implemented vocabulary. 005H keeps the
  application status unchanged and stores rejection-note status separately until a future
  appraisal/sanction rejection slice defines the status transition.
- Rejection-note send is metadata-only and does not notify borrowers.
