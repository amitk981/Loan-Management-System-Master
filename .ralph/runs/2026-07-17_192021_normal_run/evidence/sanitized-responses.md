# Sanitized Public Response Shapes

First successful §31.4 response data:

```json
{
  "disbursement_id": "<uuid>",
  "bank_transfer_status": "successful",
  "loan_account_status": "active",
  "disbursement_advice_communication_id": "<stable-pending-uuid>"
}
```

Exact-key/payload/actor §45.2 replay data:

```json
{
  "idempotency_replayed": true,
  "original_response": {
    "disbursement_id": "<same-uuid>",
    "bank_transfer_status": "successful",
    "loan_account_status": "active",
    "disbursement_advice_communication_id": "<same-stable-pending-uuid>"
  }
}
```

Successful §27.7 checklist response data retains only the standard action projection:

```json
{
  "checklist_action_id": "<uuid>",
  "entity_type": "document_checklist",
  "entity_id": "<checklist-uuid>",
  "previous_status": "sanction_approved",
  "new_status": "ready",
  "workflow_event_id": "<uuid>",
  "available_actions": []
}
```

No bank reference, email, account number, evidence checksum, internal comment, or actor identity is
returned by these public projections.

