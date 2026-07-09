# API Response Examples: 005H Rejection Note Shell

Examples follow the standard envelope shape. UUIDs and timestamps are representative.

## Create Rejection Note

`POST /api/v1/loan-applications/{loan_application_id}/rejection-note/`

Request:

```json
{
  "rejection_stage": "credit_assessment",
  "rejection_reason_category": "eligibility",
  "detailed_reason": "Borrower does not meet active member criteria.",
  "reapply_allowed_flag": true,
  "communication_mode": "email"
}
```

Success:

```json
{
  "success": true,
  "data": {
    "rejection_note_id": "00000000-0000-0000-0000-000000000001",
    "loan_application_id": "00000000-0000-0000-0000-000000000002",
    "rejection_stage": "credit_assessment",
    "rejection_reason_category": "eligibility",
    "detailed_reason": "Borrower does not meet active member criteria.",
    "reapply_allowed_flag": true,
    "note_status": "draft",
    "prepared_by_user_id": "00000000-0000-0000-0000-000000000003",
    "approved_by_user_id": null,
    "communication_mode": "email",
    "communication_id": null,
    "sent_by_user_id": null,
    "sent_at": null,
    "created_at": "2026-07-10T01:57:23Z",
    "updated_at": "2026-07-10T01:57:23Z",
    "updated_by_user_id": "00000000-0000-0000-0000-000000000003"
  },
  "meta": {
    "request_id": "req-create-rejection-note",
    "timestamp": "2026-07-10T01:57:23Z",
    "api_version": "v1"
  }
}
```

## Send Rejection Note

`POST /api/v1/rejection-notes/{rejection_note_id}/send/`

Request:

```json
{
  "recipient_email": "borrower@example.com",
  "message_override": null
}
```

Success:

```json
{
  "success": true,
  "data": {
    "rejection_note_id": "00000000-0000-0000-0000-000000000001",
    "loan_application_id": "00000000-0000-0000-0000-000000000002",
    "rejection_stage": "credit_assessment",
    "rejection_reason_category": "eligibility",
    "detailed_reason": "Borrower does not meet active member criteria.",
    "reapply_allowed_flag": true,
    "note_status": "sent",
    "prepared_by_user_id": "00000000-0000-0000-0000-000000000003",
    "approved_by_user_id": null,
    "communication_mode": "email",
    "communication_id": null,
    "sent_by_user_id": "00000000-0000-0000-0000-000000000003",
    "sent_at": "2026-07-10T01:58:00Z",
    "created_at": "2026-07-10T01:57:23Z",
    "updated_at": "2026-07-10T01:58:00Z",
    "updated_by_user_id": "00000000-0000-0000-0000-000000000003"
  },
  "meta": {
    "request_id": "req-send-rejection-note",
    "timestamp": "2026-07-10T01:58:00Z",
    "api_version": "v1"
  }
}
```

## Guard Examples

- Staff without `applications.loan_application.complete_check`: `403 PERMISSION_DENIED`.
- Same-permission staff outside application object scope: `403 OBJECT_ACCESS_DENIED`.
- Active borrower portal token on staff rejection-note routes: `403 PERMISSION_DENIED`.
- Suspended portal account using an old token: `401 INVALID_TOKEN`.
- Draft, `incomplete_returned`, reference-generated, duplicate create: `409 INVALID_STATE_TRANSITION`.
- Empty required fields, unknown fields, duplicate send: `400 VALIDATION_ERROR`.

Side-effect guarantee: failure paths create no rejection-note row, success audit row, workflow event,
register row, reference, or visible sequence advancement. Successful send creates no
`communications` row and calls no provider.
