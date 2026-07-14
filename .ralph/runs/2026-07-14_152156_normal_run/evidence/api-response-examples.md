# API Response Examples

## Pending signature capture

```json
{
  "success": true,
  "data": {
    "signature_record_id": "<uuid>",
    "loan_document_id": "<uuid>",
    "signer_party_type": "borrower",
    "signer_party_id": "<member-uuid>",
    "signer_name_snapshot": "Signature Test Borrower",
    "signature_method": "wet_ink",
    "signature_status": "pending",
    "signed_at": null,
    "signature_mismatch_flag": false,
    "mismatch_resolution_type": null,
    "mismatch_resolution_document_id": null,
    "mismatch_resolution_document_name": null,
    "remarks": null
  },
  "meta": {"request_id": "<request-id>"},
  "error": null
}
```

## Resolved mismatch

```json
{
  "success": true,
  "data": {
    "signature_record_id": "<uuid>",
    "loan_document_id": "<uuid>",
    "signer_party_type": "borrower",
    "signer_party_id": "<member-uuid>",
    "signer_name_snapshot": "Signature Test Borrower",
    "signature_method": "wet_ink",
    "signature_status": "mismatch",
    "signed_at": null,
    "signature_mismatch_flag": true,
    "mismatch_resolution_type": "bank_verification_letter",
    "mismatch_resolution_document_id": "<document-uuid>",
    "mismatch_resolution_document_name": "bank-letter.pdf",
    "remarks": "Signed and stamped bank letter inspected."
  },
  "meta": {"request_id": "<request-id>"},
  "error": null
}
```

No response contains a storage key, download URL, checklist approval, or disbursement-readiness
fact. The concrete contract is exercised in `test_signature_mismatch_api.py`.
