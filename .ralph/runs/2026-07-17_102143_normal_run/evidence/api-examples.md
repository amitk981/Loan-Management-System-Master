# Sanitized CFC Authorisation Examples

All identifiers are synthetic and no borrower, bank-account, token, capability, or contact plaintext
is included.

## Approved

Request body:

```json
{"decision":"approved","comments":"Beneficiary and instruction verified."}
```

Response data:

```json
{
  "disbursement_id": "00000000-0000-4000-8000-000000000001",
  "authorisation_status": "approved",
  "bank_transfer_status": "pending",
  "authorised_at": "2026-07-17T05:00:00Z",
  "next_action": "record_bank_transfer"
}
```

## Rejected

```json
{
  "disbursement_id": "00000000-0000-4000-8000-000000000002",
  "authorisation_status": "rejected",
  "bank_transfer_status": "pending",
  "authorised_at": "2026-07-17T05:01:00Z",
  "next_action": "none"
}
```

## Changed or opposite replay

```json
{
  "success": false,
  "error": {
    "code": "CONFLICT",
    "message": "The disbursement already has a different terminal authorisation decision.",
    "details": {},
    "field_errors": {}
  }
}
```

Exact decision/comments replay returns the retained five-field response without another action,
audit, workflow event, or task mutation.
