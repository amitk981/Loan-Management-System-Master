# API Response Examples — 004D Nominee Validation and UI

Source contract: `docs/source/api-contracts.md` §14.1-§14.3.

## `POST /api/v1/members/{member_id}/nominees/` Success

Request:

```json
{
  "nominee_name": "Sita Patil",
  "date_of_birth": "1985-05-20",
  "gender": "female",
  "relationship_to_borrower": "Spouse",
  "pan": "ABCDE1234F",
  "aadhaar": "123412341234",
  "signature_required_flag": true
}
```

Response shape verified by `sfpcl_credit.tests.test_member_nominees_api`:

```json
{
  "success": true,
  "data": {
    "nominee_id": "uuid",
    "nominee_name": "Sita Patil",
    "date_of_birth": "1985-05-20",
    "age_at_application": 41,
    "gender": "female",
    "relationship_to_borrower": "Spouse",
    "pan": { "masked": "******234F", "can_view_full": false },
    "aadhaar": { "masked": "********1234", "can_view_full": false },
    "kyc_status": "pending",
    "minor_flag": false,
    "signature_required_flag": true,
    "created_at": "2026-07-09T05:55:00Z"
  },
  "meta": {
    "request_id": "req-create-nominee",
    "timestamp": "2026-07-09T05:55:00Z",
    "api_version": "v1"
  }
}
```

## `GET /api/v1/members/{member_id}/nominees/` Success

```json
{
  "success": true,
  "data": [
    {
      "nominee_id": "uuid",
      "nominee_name": "Sita Patil",
      "date_of_birth": "1985-05-20",
      "age_at_application": 41,
      "gender": "female",
      "relationship_to_borrower": "Spouse",
      "pan": { "masked": "******234F", "can_view_full": false },
      "aadhaar": { "masked": "********1234", "can_view_full": false },
      "kyc_status": "pending",
      "minor_flag": false,
      "signature_required_flag": true,
      "created_at": "2026-07-09T05:55:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 1,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-09T05:55:00Z",
    "api_version": "v1"
  }
}
```

## Validation Errors

Missing PAN/Aadhaar:

```json
{
  "success": false,
  "error": {
    "code": "MISSING_REQUIRED_FIELD",
    "message": "Pan is required.",
    "details": {},
    "field_errors": { "pan": "This field is required." }
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-09T05:55:00Z",
    "api_version": "v1"
  }
}
```

Invalid PAN:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_PAN_FORMAT",
    "message": "PAN format is invalid.",
    "details": {},
    "field_errors": { "pan": "PAN must match the source-defined format." }
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-09T05:55:00Z",
    "api_version": "v1"
  }
}
```

Minor nominee:

```json
{
  "success": false,
  "error": {
    "code": "NOMINEE_MINOR_NOT_ALLOWED",
    "message": "Nominee must not be a minor.",
    "details": {},
    "field_errors": { "date_of_birth": "Nominee must be at least 18 years old." }
  },
  "meta": {
    "request_id": null,
    "timestamp": "2026-07-09T05:55:00Z",
    "api_version": "v1"
  }
}
```

## Permission Split

- `GET /nominees/` without `members.nominee.read` returns `403 PERMISSION_DENIED`.
- `POST /nominees/` without `members.nominee.create` returns `403 PERMISSION_DENIED`.
- Create audit action is `members.nominee.created`; audit metadata includes member/nominee IDs,
  name, age snapshot, KYC/minor/signature flags, and keyed hashes only. It never contains full PAN
  or Aadhaar values.
