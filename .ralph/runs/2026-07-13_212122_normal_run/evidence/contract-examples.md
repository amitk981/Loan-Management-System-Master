# General Meeting Contract Evidence

Pending case projection and pending-gate detail:

```json
{
  "approval_case_id": "uuid",
  "cycle_number": 1,
  "general_meeting_approval": {
    "general_meeting_approval_id": "uuid",
    "approval_status": "pending",
    "notice_document_id": "uuid",
    "minutes_document_id": "uuid",
    "resolution_document_id": "uuid",
    "evidence_scope": "current_pending"
  }
}
```

Returned/rejected/conflict-blocked/approved terminal case projection:

```json
{
  "general_meeting_approval": {
    "general_meeting_approval_id": "uuid-frozen-on-cycle",
    "approval_status": "pending | rejected | approved",
    "evidence_scope": "cycle_frozen"
  }
}
```

Every inaccessible notice/minutes/resolution reference returns the same field text:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "field_errors": {
      "notice_document_id": "Document file was not found or is inaccessible."
    }
  }
}
```

The retained terminal logs in this evidence folder contain the executable public-interface proof.
