# Risk Assessment

Risk level: Medium.

- Selected slice: 007B-approval-case-creation-from-appraisal
- Mode: normal_run
- Data/schema impact: one additive approval-case migration; existing shells remain nullable and
  unrouted until explicitly enriched.
- Financial/authority impact: routing snapshots affect approval authority, but consume only approved
  dated resolver projections and frozen credit facts; no sanction action or money movement occurs.
- Security: adapter requires authentication, `approvals.case.create`, and application object scope;
  401/403 and no-write losers are tested.
- Concurrency/atomicity: credit facts lock application → appraisal → review history before the case
  lock; enrichment, audit, and workflow evidence share one transaction. Identical repeats are
  zero-write and conflicts are rejected.
- Manual review required: normal orchestrator review only; no owner veto applies to this Medium slice.
