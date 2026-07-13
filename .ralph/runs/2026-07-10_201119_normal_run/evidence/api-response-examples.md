# 006G API Response Examples

## Successful reviewed-appraisal submission

```http
POST /api/v1/loan-applications/00000000-0000-0000-0000-000000000001/submit-to-sanction-committee/
Authorization: Bearer <redacted>
X-Request-ID: submit-sanction-006g
Content-Type: application/json

{"remarks":"Credit Manager reviewed appraisal and recommends sanction."}
```

```json
{
  "success": true,
  "data": {
    "approval_case_id": "00000000-0000-0000-0000-000000000010",
    "loan_application_id": "00000000-0000-0000-0000-000000000001",
    "loan_appraisal_note_id": "00000000-0000-0000-0000-000000000005",
    "submission_status": "pending",
    "exception_required_flag": false,
    "submitted_by": {
      "user_id": "00000000-0000-0000-0000-000000000007",
      "full_name": "Credit Manager"
    },
    "submitted_at": "2026-07-10T20:30:00+00:00"
  },
  "meta": {
    "request_id": "submit-sanction-006g",
    "timestamp": "2026-07-10T20:30:00Z",
    "api_version": "v1"
  }
}
```

## Strict payload error

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Sanction submission failed validation.",
    "details": {},
    "field_errors": {
      "committee_id": "Unknown field."
    }
  }
}
```

## State error

Draft, review-pending, returned, rejected, missing, inconsistent-history, and repeated submissions
return HTTP 409 with `error.code = "INVALID_STATE_TRANSITION"` and create no sanction-submission
case, audit record, or workflow event.
