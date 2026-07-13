# Rejected Appraisal API Evidence

The public test `test_credit_manager_rejects_appraisal_and_creates_one_unsent_rejection_note`
executes:

```http
POST /api/v1/appraisal-notes/11111111-1111-1111-1111-111111111111/review/
X-Request-ID: reject-tracer-006f2
Content-Type: application/json

{
  "decision": "rejected",
  "review_comments": "Independent credit review completed.",
  "rejection_reason_category": "eligibility",
  "detailed_reason": "Verified appraisal facts do not meet credit criteria.",
  "reapply_allowed_flag": true,
  "communication_mode": "email"
}
```

The asserted success data links the real generated IDs:

```json
{
  "loan_appraisal_note_id": "11111111-1111-1111-1111-111111111111",
  "loan_application_id": "22222222-2222-2222-2222-222222222222",
  "appraisal_status": "rejected",
  "decision": "rejected",
  "rejection_note": {
    "rejection_note_id": "33333333-3333-3333-3333-333333333333",
    "loan_application_id": "22222222-2222-2222-2222-222222222222",
    "rejection_stage": "credit_assessment",
    "rejection_reason_category": "eligibility",
    "note_status": "draft",
    "communication_status": "not_sent",
    "sent_by_user_id": null,
    "sent_at": null
  }
}
```

UUIDs above are illustrative sanitized values; the test asserts equality among the actual response,
database row, appraisal audit, and workflow entity IDs. Executed output is in
`terminal-logs/tdd-01-rejection-tracer-green.txt` and `terminal-logs/appraisal-suite.txt`.

## Metadata redaction proof

The same test inspects `appraisal.rejected` and asserts that it contains the rejection-note UUID,
category, note state, actor/time, and request ID, while excluding `review_comments`,
`detailed_reason`, and the detailed reason text. The forced-failure test proves that rejection-note
audit or appraisal-workflow failure leaves no appraisal rejection, note, or success evidence.
