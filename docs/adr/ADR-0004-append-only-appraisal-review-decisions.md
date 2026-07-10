# ADR-0004: Append-Only Appraisal Review Decisions

## Status
Accepted

## Context

The Credit Manager review interface supports `returned`, `reviewed`, and `rejected` decisions with
a required reason in `review_comments`. `LoanAppraisalNote.review_comments` and
`last_review_decision` currently store only the latest decision. A returned appraisal can be
revised, resubmitted, and reviewed again, so the later review overwrites the original return reason.
The metadata-only audit rule correctly excludes free-text comments, which means audit/workflow rows
cannot recover the lost reason.

The source and slice contract require the return reason and prior return history to remain retained.
Copying free text into generic audit JSON would violate the same contract and broaden sensitive
text exposure.

## Decision

Every successful appraisal review action will create one immutable, appraisal-owned review-decision
record in the same transaction as the appraisal state transition and its audit/workflow evidence.
The record stores the decision, review comments, reviewer, decision time, and from/to states.

`LoanAppraisalNote.review_comments`, `last_review_decision`, `reviewed_by_user`, and `reviewed_at`
remain the latest-decision projection for simple reads and state guards. They are not the historical
record. Generic audit/workflow metadata references the immutable review-decision ID and continues
to omit free-text comments.

`AppraisalWorkflow.review(...)` remains the external module interface. Callers do not create or
mutate history rows directly, and no concrete history model becomes part of the interface.

## Consequences

- A returned decision remains explainable after maker revision, resubmission, and a later final
  review.
- Rejected decisions continue to link to the existing rejection-note record; the review decision
  and rejection note are committed or rolled back together.
- Existing rows receive only an explicitly labelled legacy latest-decision backfill; no migration
  fabricates earlier review cycles that cannot be reconstructed.
- Corrective slice `006E3-appraisal-history-and-review-authority-hardening` owns the model,
  migration, authority rule, tests, and contract update.
