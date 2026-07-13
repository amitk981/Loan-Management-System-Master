# Exact HTTP Examples

The mounted default `AppraisalWorkbench` asserted these authenticated requests:

- `POST /api/v1/loan-applications/application-1/eligibility-assessment/run/` body `{}`
- `POST /api/v1/loan-applications/application-1/loan-limit-assessment/calculate/` with source IDs,
  requested amount, calculation date, and comma-separated land IDs normalized to an array.
- `POST|PATCH /api/v1/loan-applications/application-1/appraisal-note/` with only the appraisal
  writable allowlist; response IDs, snapshots, status, TAT, and history are excluded.
- `POST /api/v1/appraisal-notes/appraisal-1/revalidate-prerequisites/` body `{}`
- `POST /api/v1/appraisal-notes/appraisal-1/submit-for-review/` body `{ "remarks": "" }`
- `POST /api/v1/appraisal-notes/appraisal-1/review/` with exact reviewed, returned, and rejected
  bodies; rejection-only fields appear only for `rejected`.
- `POST /api/v1/loan-applications/application-1/submit-to-sanction-committee/` with remarks.

Every successful mutation was followed by one GET each for eligibility, loan limit, appraisal,
and sanction case. Mounted 400, 403, and 409 responses made one write call and zero refresh calls.
See `evidence/terminal-logs/frontend-container-green.log` and `frontend-final-gates.log`.
