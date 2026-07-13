# 007H API Examples

These examples contain synthetic test data only.

## Sanction decision

`GET /api/v1/loan-applications/{loan_application_id}/sanction-decision/`

```json
{
  "success": true,
  "data": {
    "sanction_decision_id": "synthetic-uuid",
    "decision": "sanctioned",
    "sanctioned_amount": "500000.00",
    "sanctioned_tenure_months": 12,
    "interest_rate_type": "floating",
    "interest_rate_value": null,
    "repayment_date": null,
    "penal_interest_rate": null,
    "charges": {},
    "security_required_summary": "Standard member security package.",
    "conditions_precedent": null,
    "decision_reason": "Reviewed appraisal recommends approval."
  }
}
```

Before approval and after rejection the same GET returns `404 NOT_FOUND`.

## Credit Sanction Register

`GET /api/v1/credit-sanction-register/?financial_year=FY2026-27&decision=sanctioned&page=1&page_size=20`

```json
{
  "success": true,
  "data": [{
    "application_number": "LO00000701",
    "borrower_name": "Approval Queue Member",
    "borrower_type": "individual_farmer",
    "requested_amount": "500000.00",
    "eligible_amount": "500000.00",
    "recommended_amount": "500000.00",
    "sanctioned_amount": "500000.00",
    "approval_authority": "CFO: Snapshot CFO (approved); Director: Snapshot Director (approved)",
    "approver_names": ["Snapshot CFO", "Snapshot Director"],
    "approval_date": "2026-07-13",
    "decision": "sanctioned",
    "reasons": "Reviewed appraisal recommends approval.",
    "exception_reference": null,
    "conflict_abstention_details": [],
    "general_meeting_approval_reference": null
  }],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

The actual response also carries synthetic register/case/application/sanction/workflow ids,
`recorded_at`, and standard request metadata. POST is method-denied; no row mutation route exists.
