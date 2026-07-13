# 006H2 Request and State Evidence

## Writable appraisal projection

Top-level PATCH keys are exactly:

`borrower_summary`, `eligibility_summary`, `loan_limit_summary`, `recommended_amount`,
`recommended_tenure_months`, `recommended_interest_type`, `recommended_security_summary`,
`repayment_capacity_notes`, `risk_assessment`, `recommendation`.

Nested `risk_assessment` keys are exactly:

`market_risk_rating`, `operational_risk_rating`, `borrower_risk_rating`, `overall_risk_rating`,
`risk_mitigation_notes`.

IDs, frozen snapshots/provenance, status, reviewer/history/TAT, rejection/case summaries, actors,
timestamps, and `available_actions` are excluded. The focused projection test asserts exact key
order and rejects representative response-only names.

## Canonical sanction reload

`GET /api/v1/loan-applications/application-1/sanction-case/` is issued through the shared
authenticated request path. Its exact returned `approval_case_id`, application/appraisal statuses,
review-decision UUID, workflow-event UUID, submission status, exception flag, actor, timestamp,
and available actions remain server-owned. A standard 404 is treated as no pending case.

## Stale write

The sanction submit regression sends one `POST` with exactly `{ "remarks": "Submit." }`. A 409
`INVALID_STATE_TRANSITION` retains field errors and is not retried.
