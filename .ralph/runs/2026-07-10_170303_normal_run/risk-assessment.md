# Risk Assessment

Risk level: High

- Selected slice: 006E-appraisal-note-create-edit-submit
- Mode: normal_run
- Standing approval: confirmed; no owner veto exists.
- Manual review required: normal post-run/orchestrator review only.

## Risk factors and controls

- Financial recommendation and prerequisite risk: appraisal consumes only the stored eligibility
  and loan-limit public projections, snapshots their UUIDs, and cannot recompute policy, acreage,
  or eligible amounts. Recommendations above the stored limit are blocked unless the stored
  assessment already flags an exception.
- Authorization risk: create, update, nested risk update, submit, GET, and application object
  scope are independently tested. Credit Manager global scope does not grant maker permissions.
- Workflow risk: one-to-one database constraints and row locks enforce one note/risk package;
  PATCH is draft-only and submit transitions once to `review_pending`.
- Audit/privacy risk: summaries, mitigation notes, and submit remarks are excluded from audit and
  workflow evidence. Forced audit failure rolls back appraisal, risk, and workflow rows.
- Migration risk: one additive migration creates two new tables and indexes; Django check and
  `makemigrations --check --dry-run` pass. No existing table is renamed or modified destructively.
- TAT risk: due time is fixed from application creation plus two days, exact-boundary behavior is
  tested, and PATCH/submit never reset it.

## Residual risk

- A-051 records that prerequisite assessment IDs are immutable UUID snapshots rather than foreign
  keys because source §14.4 omits explicit columns and appraisal must not couple to concrete
  assessment models. Source governance may later require formal FK constraints.
- Credit Manager review and sanction submission are deliberately absent and remain queued in
  sharpened slices 006F and 006G.
