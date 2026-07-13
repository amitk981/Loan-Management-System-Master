# Exception Register API Examples

Verified by the public API tests in `test_sanction_submission_api.py` and
`test_approval_case_routing_api.py`.

## Exception enrichment

`POST /api/v1/loan-applications/{id}/approval-cases/`

```json
{
  "approval_type": "sanction",
  "amount": "400000.00",
  "reason_for_approval": "Appraisal recommended approval.",
  "force_exception_route": false,
  "business_reason": "Seasonal exception is commercially justified.",
  "risk_assessment": "Seasonal cash-flow monitoring."
}
```

Success retains the canonical approval-case response and creates one pending
`exceeds_loan_limit` register row when the frozen loan-limit flag is true. A forced within-limit
request additionally names `exception_type` as `stage_bypass` or `waiver`.

## Generated register read

`GET /api/v1/exception-register/?status=pending&exception_type=exceeds_loan_limit&page=1&page_size=10`

```json
{
  "success": true,
  "data": [
    {
      "exception_register_entry_id": "uuid",
      "approval_case_id": "uuid",
      "cycle_number": 1,
      "exception_type": "exceeds_loan_limit",
      "status": "pending",
      "case_status": "pending",
      "authority_applied_summary": "CFO: Example CFO (pending); Director: Example Director (pending)",
      "route_approvers": [
        {"role_code": "cfo", "user_id": "uuid", "full_name": "Example CFO"},
        {"role_code": "director", "user_id": "uuid", "full_name": "Example Director"}
      ],
      "required_approvers": [
        {"role_code": "cfo", "user_id": "uuid", "full_name": "Example CFO", "decision": null, "acted_at": null},
        {"role_code": "director", "user_id": "uuid", "full_name": "Example Director", "decision": null, "acted_at": null}
      ],
      "approval_actions": []
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 10,
    "total_count": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

POST returns 405; callers without `approvals.exception_register.read` receive 403.
