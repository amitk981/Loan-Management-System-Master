# Risk Assessment

## Classification

- Risk level: High
- Selected slice: `010N3-interest-portfolio-completeness-closure`
- Mode: `normal_run`
- Standing approval: active; no owner veto exists for this slice.

## Material risks and controls

- A page-one loan collection could silently omit loan 101 from a financial action. Complete
  pagination now validates every page and explicit accrual batches cover the full returned
  membership; the 101-record component and service regressions are GREEN.
- A paginated read could change count or continuation while loading and present a partial collection
  as complete. The shared pagination module rejects page, size, count, or total-page drift and
  rejects an incomplete final collection.
- A backend accrual response could omit or reorder selected membership. Each batch must return the
  same month, non-dry-run mode, count, order, and loan identifiers before it is admitted.
- A later backend denial can occur after an earlier batch persisted. The client retains completed
  rows, displays exact completed-loan and completed-batch counts, and reuses stable per-batch
  idempotency keys so an owner-authorised retry is replay-safe.
- Client permission arrays could overstate mutation authority. Controls render only from the
  backend current-user `availableActions` projection, while every request remains subject to the
  backend's permission and object-scope checks.

## Residual risk

The operation is intentionally a sequence of backend-limited batches, not one cross-batch database
transaction. A scope or transport change between batches can therefore yield a disclosed partial
completion. Independent High-risk validation should confirm the visible partial-state and stable
replay behavior remain intact across the complete frontend regression pack.
