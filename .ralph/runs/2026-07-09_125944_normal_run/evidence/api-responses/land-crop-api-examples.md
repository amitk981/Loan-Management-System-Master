# Landholding and Crop Plan API Examples

## `POST /api/v1/members/{member_id}/land-holdings/`

Request:

```json
{
  "document_type": "7_12_extract",
  "survey_number": "123/4",
  "village": "Village Name",
  "taluka": "Niphad",
  "district": "Nashik",
  "state": "Maharashtra",
  "area_acres": "5.00",
  "document_id": "11111111-1111-4111-8111-111111111111"
}
```

Response data shape:

```json
{
  "land_holding_id": "uuid",
  "document_type": "7_12_extract",
  "survey_number": "123/4",
  "village": "Village Name",
  "taluka": "Niphad",
  "district": "Nashik",
  "state": "Maharashtra",
  "area_acres": "5.00",
  "document_id": "11111111-1111-4111-8111-111111111111",
  "verification_status": "pending",
  "verified_by_user_id": null,
  "verified_at": null,
  "created_at": "2026-07-09T05:55:00Z"
}
```

## `POST /api/v1/members/{member_id}/crop-plans/`

Request:

```json
{
  "loan_application_id": "22222222-2222-4222-8222-222222222222",
  "crop_type": "grapes",
  "season": "FY2026 Kharif",
  "planned_area_acres": "5.00",
  "estimated_cost_amount": "100000.00",
  "loan_purpose_alignment": "agriculture_aligned",
  "document_id": "33333333-3333-4333-8333-333333333333"
}
```

Response data shape:

```json
{
  "crop_plan_id": "uuid",
  "loan_application_id": "22222222-2222-4222-8222-222222222222",
  "crop_type": "grapes",
  "season": "FY2026 Kharif",
  "planned_area_acres": "5.00",
  "estimated_cost_amount": "100000.00",
  "loan_purpose_alignment": "agriculture_aligned",
  "document_id": "33333333-3333-4333-8333-333333333333",
  "verification_status": "pending",
  "verified_by_user_id": null,
  "verified_at": null,
  "created_at": "2026-07-09T05:56:00Z"
}
```

## Error Examples Covered By Tests

- `401 AUTH_REQUIRED` for missing bearer token.
- `403 PERMISSION_DENIED` for users without `members.member.read` on list or `members.member.update` on create.
- `404 NOT_FOUND` for unknown or soft-deleted members.
- `400 VALIDATION_ERROR` for zero/negative acreage, missing land `document_id`, and malformed UUID fields.
