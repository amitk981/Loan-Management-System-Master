# API Examples: 006C2 Cultivated Acreage Source Hardening

## Matched Cultivated Acreage

`POST /api/v1/loan-applications/{loan_application_id}/loan-limit-assessment/calculate/`

When selected verified land acreage, the application-linked verified crop-plan acreage, and profile
cultivated acreage agree after Decimal normalization, calculation succeeds and snapshots the agreed
acreage.

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
  "meta": {
    "request_id": "req-id",
    "timestamp": "2026-07-10T00:00:00Z",
    "api_version": "v1"
  }
}
```

## Mismatched Cultivated Acreage

When applicable acreage values disagree, the endpoint returns a standard validation error and writes
no `LoanLimitAssessment`, `loan_limit.calculated` audit row, or `loan_limit_assessment` workflow
event. If a snapshot already exists, the existing GET payload remains unchanged.

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Loan-limit calculation failed validation.",
    "field_errors": {
      "cultivated_acreage": "CULTIVATED_ACREAGE_UNRESOLVED"
    }
  },
  "meta": {
    "request_id": "req-id",
    "timestamp": "2026-07-10T00:00:00Z",
    "api_version": "v1"
  }
}
```
