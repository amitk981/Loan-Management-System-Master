# Sanitized Contract Evidence

## Bank decision

A successful decision now retains and returns the exact current terminal source identities:

```json
{
  "bank_verification_decision_id": "<decision-uuid>",
  "approval_case_id": "<current-approved-case-uuid>",
  "sanction_decision_id": "<current-sanctioned-decision-uuid>",
  "decision_status": "verified",
  "entity_type": "bank_verification_decision",
  "previous_status": "pending",
  "new_status": "verified",
  "available_actions": []
}
```

When the latest case is rejected or its frozen facts are malformed, the public response is the
standard nondisclosing `403 FORBIDDEN`; decision/audit/workflow/version counts remain unchanged.

## Deficiency response

A missing, duplicate, wrong-actor/state/entity/workflow, reversed, or extra terminal response chain
returns borrower-safe state only:

```json
{
  "resolution_status": "open",
  "response": {"response_status": "evidence_invalid"},
  "resubmission_allowed": false
}
```

No workflow event id is exposed, and a crafted resubmit returns `400 VALIDATION_ERROR` without an
application transition, resolution, or success ledger.
