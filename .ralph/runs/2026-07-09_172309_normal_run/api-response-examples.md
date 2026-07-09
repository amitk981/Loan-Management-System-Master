# API Response Examples: 005A Loan Application Drafts

Examples are representative of the tested contract in
`sfpcl_credit/tests/test_loan_applications_api.py`.

## Create Draft

`POST /api/v1/loan-applications/`

```json
{
  "success": true,
  "data": {
    "loan_application_id": "ab634ec8-27dd-4f66-998e-978e2de809f3",
    "application_reference_number": null,
    "member": {
      "member_id": "0f74aa6e-9465-482d-b1b2-9c6afdf37fbb",
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
      "land_holding_id": "154cd967-2ad8-41ed-9998-27706487118d",
      "survey_number": "123/4",
      "village": "Niphad",
      "area_acres": "5.00",
      "verification_status": "pending"
    },
    "crop_plan": {
      "crop_plan_id": "ca789fee-5ab4-4d48-bad9-4ea9f67e5a5a",
      "crop_type": "grapes",
      "season": "FY2026 Kharif",
      "planned_area_acres": "5.00",
      "loan_purpose_alignment": "agriculture_aligned",
      "verification_status": "pending"
    },
    "bank_account": {
      "bank_account_id": "da63fd45-eab5-4ac7-a6e1-672a018f7c5c",
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
      "cancelled_cheque_id": "53de3936-e999-47b8-9cc9-9b8a84eb5537",
      "document_id": "24473615-308f-4651-8a63-bdea2ae01873",
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
    "application_status": "draft",
    "current_stage": "initial_loan_request",
    "completeness_status": "not_started",
    "terms_acceptance_flag": false,
    "created_at": "2026-07-09T11:58:39.294678Z",
    "created_by_user_id": "82f1e011-1bce-45a4-a6c4-3f76ce99fbba",
    "updated_at": "2026-07-09T11:58:39.294392Z",
    "updated_by_user_id": "82f1e011-1bce-45a4-a6c4-3f76ce99fbba"
  },
  "meta": {
    "request_id": "req-create-loan-draft",
    "timestamp": "2026-07-09T11:58:39.297611Z",
    "api_version": "v1"
  }
}
```

## Validation Error

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Loan application payload failed validation.",
    "details": {},
    "field_errors": {
      "bank_account_id": "Referenced record was not found for this member."
    }
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-09T12:03:00.000000Z",
    "api_version": "v1"
  }
}
```

Sensitive fields intentionally absent: PAN, Aadhaar, full account numbers,
`account_number_encrypted`, `account_number_hash`, protected token values, and
frontend-only `holder_name`.
