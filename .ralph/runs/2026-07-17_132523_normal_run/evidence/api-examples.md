# Sanitized Transfer-Success Examples

## Success / exact replay

Request fields: normalized reference `RBL-UTR-0001`, timezone-aware post-authorisation timestamp,
restricted checksum-current finance evidence, and a non-empty idempotency key.

```json
{
  "success": true,
  "data": {
    "disbursement_id": "00000000-0000-4000-8000-000000000001",
    "bank_transfer_status": "successful",
    "loan_account_status": "active",
    "disbursement_advice_communication_id": null
  }
}
```

The same normalized key/payload/actor returns the same four data fields and writes nothing.

## Changed replay

```json
{
  "success": false,
  "error": {
    "code": "CONFLICT",
    "message": "The idempotency key is already bound to a different transfer request."
  }
}
```

## Duplicate normalized reference

```json
{
  "success": false,
  "error": {
    "code": "DUPLICATE_BANK_REFERENCE",
    "message": "The bank reference already exists."
  }
}
```

Audit/workflow evidence retains only a masked reference and SHA-256 digest, not the plaintext value
shown in the sanitized request example.
