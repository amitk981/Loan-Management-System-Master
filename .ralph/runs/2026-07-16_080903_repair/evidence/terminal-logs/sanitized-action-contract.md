# Sanitized Workspace Action Contract

The public projection exposes only presentation metadata and an opaque, actor/current-state-bound
identity. Canonical objects remain server-side.

```json
{
  "action_id": "<opaque-hmac-hex>",
  "action_key": "record_borrower_signature",
  "label": "Record Borrower Signature",
  "method": "POST",
  "url": "/api/v1/loan-applications/<application-id>/documentation-workspace/actions/<opaque-action-id>/",
  "enabled": true,
  "fields": []
}
```

There is no caller-controlled `fixed_payload`, document id, checklist item id, party id, template id,
bank id, or security id. Upload actions declare a `file` field and use multipart form data. The
server rebuilds the current private command, validates the exact HMAC, and then invokes its owner.
