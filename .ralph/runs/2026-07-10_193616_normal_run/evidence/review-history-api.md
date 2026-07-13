# Multi-review history API evidence

Verified by
`AppraisalApiTests.test_returned_appraisal_can_be_revised_resubmitted_and_reviewed` in
`evidence/terminal-logs/02-review-history-green.txt` and the full appraisal suite.

After `returned`, maker PATCH, resubmit, and `reviewed`, the response retains the latest projection:

```json
{
  "decision": "reviewed",
  "review_comments": "Clarification accepted.",
  "appraisal_status": "reviewed"
}
```

The same response includes chronological immutable history:

```json
{
  "review_history": [
    {
      "appraisal_review_decision_id": "<return-decision-uuid>",
      "decision": "returned",
      "review_comments": "Clarify the seasonal repayment assumptions.",
      "reviewer": {
        "user_id": "<credit-manager-uuid>",
        "full_name": "Deputy Manager Finance"
      },
      "decided_at": "<original-return-time>",
      "from_state": "review_pending",
      "to_state": "draft",
      "history_provenance": "native"
    },
    {
      "appraisal_review_decision_id": "<final-decision-uuid>",
      "decision": "reviewed",
      "review_comments": "Clarification accepted.",
      "reviewer": {
        "user_id": "<credit-manager-uuid>",
        "full_name": "Deputy Manager Finance"
      },
      "decided_at": "<final-review-time>",
      "from_state": "review_pending",
      "to_state": "reviewed",
      "history_provenance": "native"
    }
  ]
}
```

The test re-reads the first database row after the final review and asserts its reason, reviewer,
and decision time remain exact. Audit/workflow evidence contains the matching decision UUID but not
either free-text reason.
