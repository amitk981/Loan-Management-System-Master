# API Response Examples: 005E Completeness Workbench

These examples show the implemented contract shape. UUIDs and timestamps are illustrative.

## Workbench Read With Blocking Items

`GET /api/v1/loan-applications/{loan_application_id}/completeness-check/`

```json
{
  "success": true,
  "data": {
    "loan_application_id": "2b271e92-7b41-4c3f-9a18-a3ec8a084e8a",
    "application_reference_number": null,
    "application_status": "submitted",
    "current_stage": "initial_loan_request",
    "completeness_status": "not_started",
    "member": {
      "member_id": "4a9eb6cc-2d86-4325-a384-c59a4cf7f012",
      "display_name": "Ramesh Patil",
      "member_type": "individual_farmer",
      "folio_number": "FOL-005A"
    },
    "required_checklist_items": [
      {
        "document_type": "borrower_pan",
        "required_flag": true,
        "submission_status": "submitted",
        "verification_status": "rejected",
        "latest_application_document_id": "28ae3d5c-7d44-4f20-9845-2e9bff964791",
        "latest_version_number": 2,
        "complete": false,
        "reason_code": "not_verified"
      },
      {
        "document_type": "crop_plan",
        "required_flag": true,
        "submission_status": "pending",
        "verification_status": "pending",
        "latest_application_document_id": null,
        "latest_version_number": null,
        "complete": false,
        "reason_code": "missing_metadata"
      }
    ],
    "blocking_document_types": ["borrower_pan", "crop_plan"],
    "can_generate_reference": false
  },
  "meta": {
    "request_id": "req-completeness-workbench",
    "api_version": "v1"
  }
}
```

## Completeness Pass Success

`POST /api/v1/loan-applications/{loan_application_id}/completeness-check/pass/`

```json
{
  "success": true,
  "data": {
    "loan_application_id": "2b271e92-7b41-4c3f-9a18-a3ec8a084e8a",
    "application_reference_number": "LO00000001",
    "application_status": "reference_generated",
    "current_stage": "credit_assessment",
    "completeness_status": "complete",
    "loan_request_register_entry": {
      "loan_request_register_entry_id": "5ac0a80b-9dc6-40d6-90b8-d8e89cc4c7e7",
      "loan_application_id": "2b271e92-7b41-4c3f-9a18-a3ec8a084e8a",
      "application_reference_number": "LO00000001",
      "member_id": "4a9eb6cc-2d86-4325-a384-c59a4cf7f012",
      "register_status": "reference_generated",
      "requested_amount": "400000.00",
      "purpose_category": "crop_production",
      "current_stage": "credit_assessment"
    }
  },
  "meta": {
    "request_id": "req-completeness-pass",
    "api_version": "v1"
  }
}
```

## Completeness Pass Validation Failure

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Completeness check failed validation.",
    "field_errors": {
      "required_checklist_items": [
        {
          "document_type": "borrower_pan",
          "reason_code": "missing_metadata",
          "submission_status": "pending",
          "verification_status": "pending"
        }
      ]
    }
  },
  "meta": {
    "request_id": "req-completeness-fail",
    "api_version": "v1"
  }
}
```

Sensitive values intentionally absent from examples and implementation responses: raw file bytes,
storage keys, checksums, PAN, Aadhaar, full bank values, encrypted tokens, and hashes.
