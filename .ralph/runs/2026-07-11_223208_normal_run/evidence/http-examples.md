# Credit workbench HTTP contract examples

After any successful mutation the production container awaits exactly these reads for the selected
application, once each:

- `GET /api/v1/loan-applications/{id}/eligibility-assessment/`
- `GET /api/v1/loan-applications/{id}/loan-limit-assessment/`
- `GET /api/v1/loan-applications/{id}/appraisal-note/`
- `GET /api/v1/loan-applications/{id}/sanction-case/`

Representative writes retained by the container:

- `POST /api/v1/loan-applications/{id}/eligibility-assessment/run/` with `{}`
- `POST /api/v1/loan-applications/{id}/loan-limit-assessment/calculate/` with the five stored-source
  fields and `land_holding_ids` projected from comma-separated input to a string array
- `PATCH /api/v1/loan-applications/{id}/appraisal-note/` using only `projectAppraisalDraft`'s
  top-level and nested risk allowlists
- `POST /api/v1/appraisal-notes/{id}/review/` with decision/comments and rejection fields only for
  `rejected`
- `POST /api/v1/loan-applications/{id}/submit-to-sanction/` with remarks

The authenticated client performs no automatic retry. A `400`, `403`, or `409` leaves the current
resource projection in place and renders the returned error through the container boundary.
