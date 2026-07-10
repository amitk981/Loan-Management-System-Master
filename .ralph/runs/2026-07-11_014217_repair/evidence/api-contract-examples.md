# Sanction Handoff API Examples

## Successful POST and subsequent GET data

Both endpoints return the same backend-owned projection inside the standard success envelope:

```json
{
  "approval_case_id": "<case-uuid>",
  "loan_application_id": "<application-uuid>",
  "loan_appraisal_note_id": "<appraisal-uuid>",
  "appraisal_review_decision_id": "<review-uuid>",
  "workflow_event_id": "<workflow-event-uuid>",
  "application_status": "submitted_to_sanction_committee",
  "appraisal_status": "submitted_to_sanction_committee",
  "submission_status": "pending",
  "exception_required_flag": false,
  "submitted_by": {"user_id": "<actor-uuid>", "full_name": "Credit Manager"},
  "submitted_at": "<iso-8601>",
  "available_actions": []
}
```

`submission_remarks`, review comments, appraisal summaries, and risk notes are absent.

## Error paths

- Malformed JSON and JSON arrays: `400 VALIDATION_ERROR` standard envelope.
- Existing application with no pending case: `404 NOT_FOUND` standard envelope.
- Application outside the Credit Manager object boundary: `403 OBJECT_ACCESS_DENIED`.
- Duplicate submission: `409 INVALID_STATE_TRANSITION` with no duplicate evidence.

Verified by the successful-submit/read, scoped-read, and malformed/non-object JSON tests in
`test_sanction_submission_api.py`; the focused green log records all ten sanction tests.
