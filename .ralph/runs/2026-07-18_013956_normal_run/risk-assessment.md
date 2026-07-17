# Risk Assessment

Risk level: High

- Historical persistence: the receipt's physical table, primary key, unique relations, constraint,
  and genuine row are preserved through a reversible state-only owner transfer. Generated SQL
  performs no receipt-table or receipt-data operation.
- Migration graph: one communications migration depends on the current disbursements leaf, creates
  one outbox table, reverses cleanly, and reapplies without duplicate state. Migration sync is green.
- Idempotency: Manual/Fake identity no longer includes mutable payload. Fresh instances under one
  key converge on one logical external id; Future forwards the key contract and rejection remains
  retryable. Durable payload-conflict/crash/race closure remains explicitly owned by 009H3B.
- Dependency direction: communications models/adapters contain no executable disbursements import.
  The legacy disbursements receipt name is a shallow alias to the one canonical model.
- Public behavior: all retained 009H2 success, replay, provider rejection, role/object scope,
  current-truth, safe-audit, and no-financial-side-effect tests remain green.
- Privacy: the new outbox is protected persistence and intentionally contains recipient/rendered
  truth for future dispatch; this slice adds no read route, serializer, log, or audit exposure.
- Scope controls: one migration, no frontend/API/dependency/permission change, no source/protected
  edit, and no real provider/network call.

Residual risk: 009H3B must atomically freeze/populate the outbox before dispatch and prove both
acceptance crash windows plus PostgreSQL five-caller behavior. This slice does not claim that
terminal closure.

Independent orchestrator review remains required for the complete suite, coverage floor, protected
paths, and diff limits before commit.
