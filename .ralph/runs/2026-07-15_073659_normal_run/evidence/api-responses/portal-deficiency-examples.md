# Portal Deficiency API Examples

Identifiers and timestamps below are representative. Exact response shapes are asserted by
`test_portal_deficiency_response_api.py`.

## GET own open deficiencies — 200

```json
{
  "success": true,
  "data": {
    "loan_application_id": "11111111-1111-4111-8111-111111111111",
    "application_reference_number": "LA-2026-000042",
    "application_status": "incomplete_returned",
    "resubmission_allowed": true,
    "items": [{
      "deficiency_id": "22222222-2222-4222-8222-222222222222",
      "item_code": "six_month_bank_statement",
      "deficiency_type": "missing_document",
      "description": "Upload the missing six-month bank statement.",
      "resolution_status": "open",
      "raised_at": "2026-07-15T07:00:00Z",
      "upload_contract": {
        "document_category": "finance",
        "sensitivity_level": "confidential",
        "allowed_extensions": ["pdf", "jpg", "jpeg", "png"],
        "max_size_bytes": 5242880
      },
      "response": null
    }]
  },
  "meta": {"request_id": "read-1", "timestamp": "2026-07-15T07:01:00Z", "api_version": "v1"}
}
```

## POST multipart response upload — 200

```json
{
  "success": true,
  "data": {
    "deficiency_id": "22222222-2222-4222-8222-222222222222",
    "response_status": "responded",
    "response": {
      "deficiency_response_id": "33333333-3333-4333-8333-333333333333",
      "response_status": "responded",
      "response_remark": "Replacement statement attached.",
      "document": {
        "document_id": "44444444-4444-4444-8444-444444444444",
        "file_name": "statement.pdf",
        "mime_type": "application/pdf",
        "file_size_bytes": 128,
        "checksum_sha256": "<sha256>",
        "uploaded_at": "2026-07-15T07:02:00Z",
        "action_url": "/api/v1/portal/applications/11111111-1111-4111-8111-111111111111/deficiencies/22222222-2222-4222-8222-222222222222/download/"
      },
      "responded_at": "2026-07-15T07:02:00Z"
    },
    "document": {
      "document_id": "44444444-4444-4444-8444-444444444444",
      "file_name": "statement.pdf",
      "mime_type": "application/pdf",
      "file_size_bytes": 128,
      "checksum_sha256": "<sha256>",
      "uploaded_at": "2026-07-15T07:02:00Z"
    }
  },
  "meta": {"request_id": "upload-1", "timestamp": "2026-07-15T07:02:00Z", "api_version": "v1"}
}
```

## POST resubmit — 200

```json
{
  "success": true,
  "data": {
    "loan_application_id": "11111111-1111-4111-8111-111111111111",
    "application_status": "submitted",
    "completeness_status": "not_started",
    "current_stage": "initial",
    "pending_with": "SFPCL",
    "responded_deficiency_count": 1
  },
  "meta": {"request_id": "resubmit-1", "timestamp": "2026-07-15T07:03:00Z", "api_version": "v1"}
}
```

## Resubmit before every open deficiency is addressed — 400

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Every mandatory deficiency must be addressed before resubmission.",
    "details": {},
    "field_errors": {
      "deficiencies": "Every open deficiency must have a current replacement document before resubmission."
    }
  },
  "meta": {"request_id": null, "timestamp": "2026-07-15T07:03:00Z", "api_version": "v1"}
}
```

Cross-member read, upload, resubmit, and download attempts use the same nondisclosing `404
NOT_FOUND` envelope and are covered by the focused backend suite.
