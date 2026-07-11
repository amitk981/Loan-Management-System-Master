# Epic 006 API Happy-Path Evidence

The focused Django integration test exercised the real public endpoints and asserted these
response facts on one application chain:

- Eligibility: `200`, `overall_result=eligible`, retained assessment UUID.
- Loan limit: `200`, `amount_within_limit_flag=true`, `exception_required_flag=false`, retained
  loan-limit UUID.
- Appraisal create/PATCH/submit: `200`, exact eligibility/limit UUIDs, draft then review-pending.
- Review: preparer `403`; Credit Manager `200 reviewed`, retained review-decision UUID.
- Sanction: permission-only and pre-reviewed attempts denied; reviewed Credit Manager submission
  `200`, exact application/appraisal/review/workflow/case UUID chain, `pending`, exception false.
- Readback: sanction-case GET data exactly equals submission data.
- Repeat: `409 INVALID_STATE_TRANSITION`; approval-case, sanction audit, and workflow counts remain
  `(1, 1, 1)`.

Executable evidence: `terminal-logs/backend-tracer-final.log` and
`terminal-logs/backend-coverage.log`.
