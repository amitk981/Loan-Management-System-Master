# API Response Examples: 005D Application Document Checklist

These examples show the implemented response shapes. Values are representative test data; no raw
file bytes, storage keys, checksums, full PAN/Aadhaar/bank values, encrypted tokens, or hashes are
included.

## Checklist Read

`GET /api/v1/loan-applications/{loan_application_id}/document-checklist/`

```json
{
  "success": true,
  "data": {
    "loan_application_id": "11111111-1111-4111-8111-111111111111",
    "items": [
      {
        "document_type": "borrower_pan",
        "required_flag": true,
        "submission_status": "submitted",
        "verification_status": "verified",
        "latest_application_document_id": "22222222-2222-4222-8222-222222222222",
        "latest_version_number": 1
      },
      {
        "document_type": "six_month_bank_statement",
        "required_flag": true,
        "submission_status": "pending",
        "verification_status": "pending",
        "latest_application_document_id": null,
        "latest_version_number": null
      }
    ]
  },
  "meta": {
    "request_id": "req-checklist",
    "timestamp": "2026-07-09T14:00:00Z",
    "api_version": "v1"
  }
}
```

## Attach Application Document Metadata

`POST /api/v1/loan-applications/{loan_application_id}/application-documents/`

```json
{
  "success": true,
  "data": {
    "application_document_id": "22222222-2222-4222-8222-222222222222",
    "loan_application_id": "11111111-1111-4111-8111-111111111111",
    "document_type": "borrower_pan",
    "party_type": "borrower",
    "party_id": "33333333-3333-4333-8333-333333333333",
    "document_file": {
      "document_id": "44444444-4444-4444-8444-444444444444",
      "file_name": "borrower-pan.pdf",
      "mime_type": "application/pdf",
      "file_size_bytes": 256,
      "sensitivity_level": "restricted",
      "uploaded_at": "2026-07-09T14:00:00Z"
    },
    "required_flag": true,
    "submission_status": "submitted",
    "verification_status": "pending",
    "verified_by_user_id": null,
    "verified_at": null,
    "remarks": "PAN copy received at branch.",
    "version_number": 1,
    "created_at": "2026-07-09T14:00:00Z",
    "created_by_user_id": "55555555-5555-4555-8555-555555555555",
    "updated_at": "2026-07-09T14:00:00Z",
    "updated_by_user_id": "55555555-5555-4555-8555-555555555555"
  },
  "meta": {
    "request_id": "req-app-doc-upload",
    "timestamp": "2026-07-09T14:00:00Z",
    "api_version": "v1"
  }
}
```

## Verify Application Document

`POST /api/v1/application-documents/{application_document_id}/verify/`

```json
{
  "success": true,
  "data": {
    "application_document_id": "22222222-2222-4222-8222-222222222222",
    "loan_application_id": "11111111-1111-4111-8111-111111111111",
    "document_type": "borrower_pan",
    "party_type": "borrower",
    "party_id": "33333333-3333-4333-8333-333333333333",
    "document_file": {
      "document_id": "44444444-4444-4444-8444-444444444444",
      "file_name": "borrower-pan.pdf",
      "mime_type": "application/pdf",
      "file_size_bytes": 256,
      "sensitivity_level": "restricted",
      "uploaded_at": "2026-07-09T14:00:00Z"
    },
    "required_flag": true,
    "submission_status": "submitted",
    "verification_status": "verified",
    "verified_by_user_id": "55555555-5555-4555-8555-555555555555",
    "verified_at": "2026-07-09T14:05:00Z",
    "remarks": "PAN name matches member profile.",
    "version_number": 1,
    "created_at": "2026-07-09T14:00:00Z",
    "created_by_user_id": "55555555-5555-4555-8555-555555555555",
    "updated_at": "2026-07-09T14:05:00Z",
    "updated_by_user_id": "55555555-5555-4555-8555-555555555555"
  },
  "meta": {
    "request_id": "req-app-doc-verify",
    "timestamp": "2026-07-09T14:05:00Z",
    "api_version": "v1"
  }
}
```
