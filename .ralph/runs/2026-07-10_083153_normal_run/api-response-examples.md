# Loan-Limit Stored Snapshot API Examples

## Stored read

Request:

```http
GET /api/v1/loan-applications/11111111-1111-4111-8111-111111111111/loan-limit-assessment/
Authorization: Bearer <staff access token>
X-Request-ID: req-read-loan-limit-snapshot
```

Response shape verified by
`test_loan_limit_read_returns_immutable_stored_snapshot_without_evidence`:

```json
{
  "success": true,
  "data": {
    "loan_limit_assessment_id": "22222222-2222-4222-8222-222222222222",
    "loan_application_id": "11111111-1111-4111-8111-111111111111",
    "member_id": "33333333-3333-4333-8333-333333333333",
    "shareholding_id": "44444444-4444-4444-8444-444444444444",
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
      "loan_policy_config_id": "55555555-5555-4555-8555-555555555555",
      "policy_name": "Short Term Crop Loan Policy",
      "board_approval_reference": "BOARD/2026/006C"
    },
    "calculated_by_user_id": "66666666-6666-4666-8666-666666666666",
    "calculated_at": "2026-07-10T08:35:00Z",
    "warnings": [
      {
        "code": "REQUESTED_AMOUNT_EXCEEDS_LIMIT",
        "message": "Requested amount exceeds final eligible loan amount."
      }
    ]
  },
  "meta": {
    "request_id": "req-read-loan-limit-snapshot",
    "timestamp": "2026-07-10T08:36:00Z",
    "api_version": "v1"
  }
}
```

The integration test mutates the live application amount, share count/value, land acreage, crop
area, policy version/rules/name/Board reference, then verifies this GET data remains identical. A
later successful calculate replaces the same assessment UUID and its complete stored snapshot.

## Missing assessment

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Loan-limit assessment was not found."
  },
  "meta": {
    "request_id": "request-id",
    "timestamp": "2026-07-10T08:36:00Z",
    "api_version": "v1"
  }
}
```

Read permission denial and application object-scope denial use the standard
`PERMISSION_DENIED`/`OBJECT_ACCESS_DENIED` envelopes. All GET cases create no loan-limit audit or
workflow evidence.
