# 011B API Examples

## Assess expired default

```http
POST /api/v1/default-cases/00000000-0000-0000-0000-000000000001/assess/
Authorization: Bearer <Credit Assessment Team session>
Content-Type: application/json
```

```json
{
  "assessment_type": "post_grace",
  "payment_failure_classification": "non_intentional",
  "reason_summary": "Documented operational cause supplied by the assessor.",
  "evidence_document_ids": ["00000000-0000-0000-0000-000000000002"],
  "borrower_interaction_summary": "Borrower interaction was documented.",
  "recommended_action": "grant_extension"
}
```

The standard success envelope returns the assessment ID, case ID, retained request facts,
`assessed_by_user_id`, and server `assessed_at`. Existing detail/list items additionally return:

```json
{
  "grace_state": "expired",
  "current_assessment": {
    "assessment_type": "post_grace",
    "payment_failure_classification": "non_intentional"
  },
  "available_actions": []
}
```

Before assessment, an authorised assessor receives `available_actions: ["assess"]`. Early or paid
cases return `409 CONFLICT`; invalid/missing/foreign evidence returns `400 VALIDATION_ERROR`;
inaccessible identities return `404 NOT_FOUND`; missing authority returns `403 FORBIDDEN`.
