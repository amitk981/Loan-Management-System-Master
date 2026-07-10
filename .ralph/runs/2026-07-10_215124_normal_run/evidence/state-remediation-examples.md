# Legacy Appraisal Remediation Examples

## State outcomes

| Prior state | Legacy action result | Review authority | Downstream result |
|---|---|---|---|
| `draft` | Pins current eligible projections; remains `draft` | No review inherited | Maker may submit for review |
| `review_pending` | Pins current eligible projections; remains `review_pending` | No terminal review inherited | Credit Manager must decide independently |
| `reviewed` | Pins current projections; returns to `draft` | Latest mutable decision/reviewer/time/comments cleared; immutable history retained | Sanction returns `409` until maker resubmits and a fresh review succeeds |
| `rejected` | `409 INVALID_STATE_TRANSITION` | Unchanged | Governed manual repair required |
| `submitted_to_sanction_committee` | `409 INVALID_STATE_TRANSITION` | Unchanged | Governed manual repair required |

Verified by `AppraisalApiTests.test_legacy_unverified_draft_requires_scoped_revalidation_before_submit`,
`test_legacy_review_pending_revalidation_pins_facts_and_stays_pending`,
`test_legacy_reviewed_revalidation_requires_fresh_review_before_sanction`, and
`test_revalidation_rejects_malformed_scope_and_terminal_states_without_writes`.

## Migration outcomes

- Returned then resubmitted: reconstructs one `returned`, `review_pending -> draft`,
  `legacy_latest_only` history row.
- Reviewed then submitted: reconstructs one `reviewed`, `review_pending -> reviewed`,
  `legacy_latest_only` history row.
- Exact latest row already present: adds nothing.
- Incomplete latest projection: adds nothing.
- Earlier native cycle present: preserves it and adds only the complete missing latest projection.
- Reverse then second forward: preserves rows and adds no duplicates.

Verified by `LegacyAppraisalRemediationMigrationTests`; full output is in
`evidence/terminal-logs/006E4-migration-all-green.log`.
