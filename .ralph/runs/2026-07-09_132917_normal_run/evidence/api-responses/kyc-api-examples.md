# KYC API Examples

## Create Profile

`POST /api/v1/kyc-profiles/`

```json
{
  "success": true,
  "data": {
    "kyc_profile_id": "uuid",
    "party_type": "member",
    "party_id": "uuid",
    "kyc_status": "pending",
    "ckyc_consent_flag": true,
    "beneficial_ownership_verified_flag": false,
    "risk_rating": "low",
    "last_verified_at": null,
    "last_verified_by_user_id": null,
    "rekyc_due_date": null,
    "rejection_reason": null,
    "documents": []
  }
}
```

## Upload Document

`POST /api/v1/kyc-profiles/{kyc_profile_id}/documents/`

```json
{
  "success": true,
  "data": {
    "kyc_document_id": "uuid",
    "kyc_profile_id": "uuid",
    "document_type": "pan",
    "document_id": "uuid",
    "file_name": "borrower-pan.pdf",
    "mime_type": "application/pdf",
    "file_size_bytes": 18,
    "sensitivity_level": "restricted",
    "self_attested_flag": true,
    "verification_status": "pending",
    "verified_by_user_id": null,
    "verified_at": null,
    "remarks": null
  }
}
```

## Verify Document

`POST /api/v1/kyc-documents/{kyc_document_id}/verify/`

```json
{
  "success": true,
  "data": {
    "document_type": "pan",
    "verification_status": "verified",
    "verified_by_user_id": "uuid",
    "remarks": "Document verified against original."
  }
}
```

Evidence: `evidence/terminal-logs/backend-kyc-red.log` and
`evidence/terminal-logs/backend-kyc-green.log`.
