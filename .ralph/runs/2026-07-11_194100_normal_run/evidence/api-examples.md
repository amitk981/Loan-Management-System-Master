# Completeness API Examples

## Authoritative completeness read

`GET /api/v1/loan-applications/{id}/completeness-check/` returns application, nominee, blocker,
reference, workflow facts, completeness annotations, and four §44-shaped `available_actions`.

```json
{
  "success": true,
  "data": {
    "loan_application_id": "uuid",
    "application_status": "submitted",
    "blocking_document_types": ["borrower_pan"],
    "can_generate_reference": false,
    "available_actions": [
      {
        "action_code": "pass_completeness",
        "label": "Generate reference number",
        "enabled": false,
        "disabled_reason": "Required nominee and document checks must be complete.",
        "required_permission": "applications.loan_application.complete_check"
      },
      {
        "action_code": "return_with_deficiencies",
        "label": "Return for deficiency",
        "enabled": true,
        "disabled_reason": null,
        "required_permission": "applications.loan_application.complete_check"
      }
    ]
  }
}
```

The deficiency read returns the same action projection beside the complete open/resolved history.
The document-checklist read remains authoritative for each required row's submission status,
verification status, and latest document metadata. The client joins the projections by document
type and displays an error instead of choosing one when they disagree.

## Exact mutation requests

```http
POST /api/v1/loan-applications/{id}/completeness-check/pass/
Content-Type: application/json

{}
```

```json
{
  "communication_mode": "email",
  "message": "Please submit the missing document.",
  "items": [{"item_code": "borrower_pan", "remarks": "Current PAN copy is missing."}]
}
```

```json
{"resolution_notes": "Verified replacement received."}
```

```json
{
  "rejection_stage": "completeness",
  "rejection_reason_category": "missing_document",
  "detailed_reason": "Required evidence cannot be supplied.",
  "reapply_allowed_flag": true,
  "communication_mode": "email"
}
```

After success the container re-reads the submitted queue, returned queue, document checklist,
completeness projection, and full deficiency history. A `409 INVALID_STATE_TRANSITION` is shown
after exactly one request and does not perform these reads until the user chooses Refresh.
