# 007G API Examples

Identifiers are synthetic review examples; no personal or production data is present.

## Record approved evidence

```http
POST /api/v1/loan-applications/10000000-0000-0000-0000-000000000001/general-meeting-approval/
Authorization: Bearer <token>
Content-Type: application/json
X-Request-ID: req-general-meeting-approved
```

```json
{
  "related_party_type": "director_relative",
  "related_party_user_id": "20000000-0000-0000-0000-000000000002",
  "relationship_description": "Borrower is a relative of a Director.",
  "meeting_date": "2026-07-15",
  "notice_document_id": "30000000-0000-0000-0000-000000000003",
  "minutes_document_id": "40000000-0000-0000-0000-000000000004",
  "resolution_document_id": "50000000-0000-0000-0000-000000000005",
  "approval_status": "approved"
}
```

Representative success data:

```json
{
  "success": true,
  "data": {
    "general_meeting_approval_id": "60000000-0000-0000-0000-000000000006",
    "loan_application_id": "10000000-0000-0000-0000-000000000001",
    "related_party_type": "director_relative",
    "related_party_user_id": "20000000-0000-0000-0000-000000000002",
    "relationship_description": "Borrower is a relative of a Director.",
    "meeting_date": "2026-07-15",
    "notice_document_id": "30000000-0000-0000-0000-000000000003",
    "minutes_document_id": "40000000-0000-0000-0000-000000000004",
    "resolution_document_id": "50000000-0000-0000-0000-000000000005",
    "approval_status": "approved",
    "recorded_by_user_id": "70000000-0000-0000-0000-000000000007",
    "recorded_at": "2026-07-13T13:00:00Z",
    "supersedes_general_meeting_approval_id": null
  },
  "meta": {
    "request_id": "req-general-meeting-approved",
    "timestamp": "2026-07-13T13:00:00Z",
    "api_version": "v1"
  }
}
```

Exact replay returns the same evidence id and makes no new business write. A changed outcome
returns a new id with `supersedes_general_meeting_approval_id` set to the prior id.

## Missing final evidence

```json
{
  "success": false,
  "error": {
    "code": "GENERAL_MEETING_EVIDENCE_REQUIRED",
    "message": "Approved general meeting evidence is required before final sanction.",
    "details": {
      "approval_case_id": "80000000-0000-0000-0000-000000000008",
      "cycle_number": 1,
      "general_meeting_approval_id": null,
      "approval_status": null
    },
    "field_errors": {}
  },
  "meta": {
    "request_id": "req-final-approval",
    "timestamp": "2026-07-13T13:05:00Z",
    "api_version": "v1"
  }
}
```

Pending and rejected current outcomes use `GENERAL_MEETING_APPROVAL_PENDING` and
`GENERAL_MEETING_APPROVAL_REJECTED`, with the current evidence id/status in `details`.
