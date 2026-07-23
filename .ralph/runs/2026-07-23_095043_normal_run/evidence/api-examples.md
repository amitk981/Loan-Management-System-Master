# KYC Correction API Examples

## Borrower submission response

```json
{
  "success": true,
  "data": {
    "kyc_correction_request_id": "synthetic-uuid",
    "status": "submitted",
    "changes": {"pan": "******234F"},
    "reason": "My verified PAN record is stale.",
    "rejection_reason": null,
    "submitted_at": "2026-07-23T08:00:00Z",
    "review_started_at": null,
    "decided_at": null,
    "evidence": [
      {
        "document_id": "synthetic-document-uuid",
        "file_name": "corrected-pan.pdf",
        "mime_type": "application/pdf",
        "uploaded_at": "2026-07-23T08:00:00Z"
      }
    ]
  }
}
```

## Cross-member denial

```json
{
  "success": false,
  "error": {
    "code": "OBJECT_ACCESS_DENIED",
    "message": "You cannot submit a correction for this member."
  }
}
```

The executable response assertions are in
`sfpcl_credit.tests.test_portal_kyc_correction_api`. Examples are synthetic and intentionally omit
reviewer identity, internal notes, storage keys, and full protected identity values.
