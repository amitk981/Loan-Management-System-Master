# API Response Examples

Slice: `005F-deficiency-creation-and-resolution`

## Return With Deficiencies

Request:

```http
POST /api/v1/loan-applications/{loan_application_id}/return-with-deficiencies/
Authorization: Bearer <staff access token>
X-Request-ID: req-return-deficiencies
Content-Type: application/json
```

```json
{
  "communication_mode": "email",
  "message": "Please submit corrected documents to proceed.",
  "items": [
    {
      "item_code": "borrower_pan",
      "remarks": "PAN name does not match the member profile."
    }
  ]
}
```

Success data includes the submitted application, `completeness_status = incomplete`, and open
deficiency rows. Invalid arbitrary item codes return `400 VALIDATION_ERROR`; draft or
reference-generated applications return `409 INVALID_STATE_TRANSITION`.

## List Deficiencies

```http
GET /api/v1/loan-applications/{loan_application_id}/deficiencies/
Authorization: Bearer <staff access token>
```

Success data:

```json
{
  "loan_application_id": "uuid",
  "items": [
    {
      "deficiency_id": "uuid",
      "loan_application_id": "uuid",
      "item_code": "borrower_pan",
      "deficiency_type": "not_verified",
      "source_reason_code": "not_verified",
      "description": "borrower pan is submitted but not verified.",
      "remarks": "PAN name does not match the member profile.",
      "resolution_status": "open",
      "raised_by_user_id": "uuid",
      "raised_at": "2026-07-09T15:30:00Z",
      "resolved_by_user_id": null,
      "resolved_at": null,
      "resolution_notes": ""
    }
  ]
}
```

## Resolve Deficiency

Request:

```http
POST /api/v1/deficiencies/{deficiency_id}/resolve/
Authorization: Bearer <staff access token>
X-Request-ID: req-resolve-deficiency
Content-Type: application/json
```

```json
{
  "resolution_notes": "Borrower uploaded replacement PAN and it was verified."
}
```

Success data returns the same deficiency item with `resolution_status = resolved`,
`resolved_by_user_id`, `resolved_at`, and `resolution_notes`.

Evidence tests verify these responses do not expose PAN, Aadhaar, full bank account values, storage
keys, checksums, encrypted tokens, hashes, or raw file bytes.
