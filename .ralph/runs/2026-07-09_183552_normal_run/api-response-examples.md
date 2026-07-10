# API Response Examples

## Generate Reference Success

`POST /api/v1/loan-applications/{loan_application_id}/generate-reference/`

```json
{
  "success": true,
  "data": {
    "loan_application_id": "7f4a0d57-8a6e-4aa6-bb30-62918237e03a",
    "application_reference_number": "LO00000001",
    "member": {
      "member_id": "67f0e0aa-b3f4-4f6b-8a0a-8f6f7c8d3f41",
      "display_name": "Ramesh Patil",
      "member_type": "individual_farmer",
      "folio_number": "FOL-005A",
      "membership_status": "active",
      "kyc_status": "verified"
    },
    "application_status": "reference_generated",
    "current_stage": "credit_assessment",
    "completeness_status": "complete",
    "loan_request_register_entry": {
      "loan_request_register_entry_id": "04d13eb6-9e42-4011-8cb8-608d22633b71",
      "loan_application_id": "7f4a0d57-8a6e-4aa6-bb30-62918237e03a",
      "application_reference_number": "LO00000001",
      "member_id": "67f0e0aa-b3f4-4f6b-8a0a-8f6f7c8d3f41",
      "date_received": "2026-07-09",
      "reference_generated_date": "2026-07-09",
      "received_channel": "assisted_digital",
      "register_status": "reference_generated",
      "borrower_name": "Ramesh Patil",
      "folio_number": "FOL-005A",
      "member_type": "individual_farmer",
      "requested_amount": "400000.00",
      "purpose_category": "crop_production",
      "current_stage": "credit_assessment",
      "current_owner_role": "Deputy Manager / Credit Manager",
      "eligibility_status": "pending",
      "sanction_status": "pending",
      "documentation_status": "pending",
      "disbursement_status": "pending",
      "created_at": "2026-07-09T13:30:00.000000Z"
    }
  },
  "meta": {
    "request_id": "req-generate-reference",
    "timestamp": "2026-07-09T13:30:00.000000Z",
    "api_version": "v1"
  }
}
```

Sensitive fields are intentionally absent: no PAN, Aadhaar, full bank account numbers, encrypted
token values, hashes, or raw document/file bytes.

## Duplicate Or Invalid State

```json
{
  "success": false,
  "error": {
    "code": "INVALID_STATE_TRANSITION",
    "message": "Action generate_reference is not allowed from state reference_generated.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-09T13:30:00.000000Z",
    "api_version": "v1"
  }
}
```

## Missing Permission

```json
{
  "success": false,
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "You do not have permission to complete-check loan applications.",
    "details": {},
    "field_errors": {}
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-09T13:30:00.000000Z",
    "api_version": "v1"
  }
}
```
