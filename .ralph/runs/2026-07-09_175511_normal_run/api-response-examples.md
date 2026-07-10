# API Response Examples

Slice: `005B-application-submit-and-status-transition`

These examples mirror the passing API regression tests in
`sfpcl_credit/tests/test_loan_applications_api.py`. IDs and timestamps are representative.

## Submit Draft Success

`POST /api/v1/loan-applications/{loan_application_id}/submit/`

```json
{
  "success": true,
  "data": {
    "loan_application_id": "11111111-1111-4111-8111-111111111111",
    "application_reference_number": null,
    "member": {
      "member_id": "22222222-2222-4222-8222-222222222222",
      "display_name": "Ramesh Patil",
      "member_type": "individual_farmer",
      "folio_number": "FOL-005A",
      "membership_status": "active",
      "kyc_status": "verified"
    },
    "application_date": "2026-07-09",
    "required_loan_amount": "400000.00",
    "requested_tenure_months": 12,
    "declared_purpose": "Crop production loan for grape cultivation",
    "purpose_category": "crop_production",
    "loan_type_requested": "short_term",
    "land_holding": {
      "land_holding_id": "33333333-3333-4333-8333-333333333333",
      "survey_number": "123/4",
      "village": "Niphad",
      "area_acres": "5.00",
      "verification_status": "pending"
    },
    "crop_plan": {
      "crop_plan_id": "44444444-4444-4444-8444-444444444444",
      "crop_type": "grapes",
      "season": "FY2026 Kharif",
      "planned_area_acres": "5.00",
      "loan_purpose_alignment": "agriculture_aligned",
      "verification_status": "pending"
    },
    "bank_account": {
      "bank_account_id": "55555555-5555-4555-8555-555555555555",
      "account_holder_name": "Ramesh Patil",
      "account_number": {
        "masked": "********9012",
        "last4": "9012",
        "can_view_full": false
      },
      "ifsc": "HDFC0001234",
      "bank_name": "HDFC Bank",
      "branch_name": "Nashik Road",
      "verification_status": "pending",
      "status": "active"
    },
    "cancelled_cheque": {
      "cancelled_cheque_id": "66666666-6666-4666-8666-666666666666",
      "document_id": "77777777-7777-4777-8777-777777777777",
      "account_number": {
        "masked": "********9012",
        "last4": "9012",
        "can_view_full": false
      },
      "ifsc": "HDFC0001234",
      "branch_name": "Nashik Road",
      "verification_status": "pending",
      "signature_mismatch_flag": false
    },
    "borrower_request_notes": "Borrower prefers assisted digital intake.",
    "application_status": "submitted",
    "current_stage": "initial_loan_request",
    "completeness_status": "not_started",
    "terms_acceptance_flag": false,
    "created_at": "2026-07-09T12:29:00Z",
    "created_by_user_id": "88888888-8888-4888-8888-888888888888",
    "submitted_at": "2026-07-09T12:30:00Z",
    "submitted_by_user_id": "88888888-8888-4888-8888-888888888888",
    "updated_at": "2026-07-09T12:30:00Z",
    "updated_by_user_id": "88888888-8888-4888-8888-888888888888"
  },
  "meta": {
    "request_id": "req-submit-loan-application",
    "timestamp": "2026-07-09T12:30:00Z",
    "api_version": "v1"
  }
}
```

Sensitive values intentionally absent: PAN, Aadhaar, full bank account numbers, encrypted token
values, and hashes.

## Submit Missing Required Facts

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Loan application payload failed validation.",
    "details": {},
    "field_errors": {
      "required_loan_amount": "Requested amount must be greater than zero.",
      "declared_purpose": "Declared purpose is required before submit.",
      "purpose_category": "Purpose category is required before submit."
    }
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-09T12:30:00Z",
    "api_version": "v1"
  }
}
```

## Submit Non-Draft Application

```json
{
  "success": false,
  "error": {
    "code": "INVALID_STATE_TRANSITION",
    "message": "Expected status draft, found submitted.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-09T12:30:00Z",
    "api_version": "v1"
  }
}
```
