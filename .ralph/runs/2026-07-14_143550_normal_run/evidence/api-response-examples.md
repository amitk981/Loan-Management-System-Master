# API Response Examples

## Pending stamp duty recorded by Compliance Team

```json
{
  "success": true,
  "data": {
    "stamp_record_id": "<uuid>",
    "loan_document_id": "<uuid>",
    "stamp_paper_amount": "500.00",
    "stamp_type": "physical",
    "stamp_number": "MH-STAMP-123",
    "stamp_purchase_date": "2026-06-22",
    "executed_date": null,
    "status": "pending",
    "remarks": "Prepared for CS verification."
  },
  "meta": {"request_id": "req-stamp-create", "timestamp": "<iso-time>", "api_version": "v1"}
}
```

## Completed notarisation recorded by Company Secretary

```json
{
  "success": true,
  "data": {
    "notary_record_id": "<uuid>",
    "loan_document_id": "<uuid>",
    "notary_name": "Test Notary",
    "notary_registration_number": "NOT-123",
    "notarised_date": "2026-06-22",
    "status": "completed",
    "evidence_document_id": "<same-application-legal-document-uuid>",
    "remarks": "Original inspected."
  },
  "meta": {"request_id": null, "timestamp": "<iso-time>", "api_version": "v1"}
}
```

## Cross-application evidence rejected

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Notarisation record failed validation.",
    "details": {},
    "field_errors": {
      "evidence_document_id": "Document file was not found or is inaccessible."
    }
  },
  "meta": {"request_id": null, "timestamp": "<iso-time>", "api_version": "v1"}
}
```

These shapes are asserted by `sfpcl_credit.tests.test_stamp_notary_api`; responses expose metadata
only and contain no storage key or download descriptor.
