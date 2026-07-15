# 008J API Examples

All identifiers and cheque values below are synthetic test data.

## Ordinary collected response

```json
{
  "success": true,
  "data": {
    "blank_dated_cheque_id": "uuid",
    "security_package_id": "uuid",
    "member_id": "uuid",
    "bank_account_id": "uuid",
    "cancelled_cheque_id": "uuid",
    "cheque_number": "******",
    "document_id": null,
    "cheque_status": "collected",
    "custody_location": null,
    "collected_at": "2026-07-14",
    "prepared_by_user_id": "uuid",
    "custodian_user_id": null,
    "custody_evidence": null
  }
}
```

## Terminal held response

`PATCH /api/v1/blank-dated-cheques/{id}/` with the exact retained material, `cheque_status: held`,
and `custody_location: CS secure cabinet` returns the same fixed mask plus the immutable distinct
Company Secretary `custodian_user_id` and plaintext-free custody evidence.

## Explicit reveal response

`POST /api/v1/blank-dated-cheques/{id}/reveal-cheque-number/` with
`{"reason":"Physical custody reconciliation"}` returns synthetic `cheque_number: 123456` and a
five-minute `expires_at` only to an authorised scoped Company Secretary. Headers include
`Cache-Control: no-store` and `Pragma: no-cache`; the audit contains the reason and field name but
not the number.

## Fail-closed examples

- Missing/pending/conflicting bank or cancelled-cheque truth: `400 VALIDATION_ERROR`, zero cheque
  and success-evidence writes.
- Read-only actor mutation: `403 FORBIDDEN` before payload parsing.
- Reveal without dedicated authority: `403 SENSITIVE_FIELD_ACCESS_DENIED` plus denial audit.
- Unavailable/tampered encryption key/ciphertext: `409 CONFLICT` plus denial audit.
- Repeated reveal in five minutes: `429 RATE_LIMITED` plus denial audit.
