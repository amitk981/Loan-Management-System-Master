# API Response Examples

Captured contract example from the green 006C endpoint tracer. IDs/timestamps are representative;
the asserted financial and boundary values are exact.

## Successful calculation above the eligible limit

```json
{
  "success": true,
  "data": {
    "loan_limit_assessment_id": "uuid",
    "loan_application_id": "uuid",
    "member_id": "uuid",
    "shareholding_id": "uuid",
    "number_of_shares": 100,
    "valuation_per_share": "2000.00",
    "share_limit_percentage": "10.0000",
    "per_share_cap_amount": "200.00",
    "shareholding_based_limit_amount": "20000.00",
    "land_area_acres": "5.00",
    "scale_of_finance_per_acre_amount": "20000.00",
    "land_based_limit_amount": "100000.00",
    "final_eligible_loan_amount": "20000.00",
    "requested_amount": "400000.00",
    "amount_within_limit_flag": false,
    "exception_required_flag": true,
    "calculation_rule_version": "loan-policy-v1.0",
    "configuration_source": {
      "type": "loan_policy_config",
      "loan_policy_config_id": "uuid",
      "policy_name": "Board-approved member loan policy",
      "board_approval_reference": "BOARD/2026/006C"
    },
    "calculated_by_user_id": "uuid",
    "calculated_at": "2026-07-10T00:00:00Z",
    "warnings": [
      {
        "code": "REQUESTED_AMOUNT_EXCEEDS_LIMIT",
        "message": "Requested amount exceeds final eligible loan amount."
      }
    ]
  },
  "error": null,
  "meta": {
    "request_id": "req-calculate-loan-limit",
    "timestamp": "2026-07-10T00:00:00Z",
    "api_version": "v1"
  }
}
```

## Blocked pending eligibility

HTTP `409`, error code `INVALID_STATE_TRANSITION`; no `LoanLimitAssessment`,
`loan_limit.calculated` audit, or `loan_limit_assessment` workflow event is created.

## Blocked missing or unresolved policy

HTTP `400`, error code `VALIDATION_ERROR`, with
`error.field_errors.loan_policy_config`; no calculation success evidence is created.
