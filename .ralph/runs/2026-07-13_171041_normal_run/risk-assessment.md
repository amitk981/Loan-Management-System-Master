# Risk Assessment

Risk level: High

- Selected slice: `007E2-conflict-authority-projection-and-scope-closure`
- Standing approval: active; no owner veto exists.
- Primary risk: sanction authority could be silently reduced or an unassigned person could learn a
  case/count. Those failures can affect lending governance and confidentiality.
- Data risk: migration 0013 replaces an over-broad derived reader index with original/effective/
  acted users and tightens declaration-reason validation. It does not rewrite immutable cases,
  actions, audits, workflows, communications, or sanctions.
- Transaction risk: the explicit projection updater runs inside every owning writer's transaction;
  a projection failure rolls back enrichment/action/application state rather than leaving split
  authority facts.
- Compatibility risk: canonical read responses add `route_approvers` and `approval_actions`, and
  replacement rows add `replacement_for_user_id`. The existing §25.2 enrichment
  `required_approvers` response remains raw/backward-compatible after a full-suite regression found
  and repaired that distinction.
- Concurrency: no new concurrency capability was declared. Existing action locks remain unchanged;
  this slice prevents duplicate identity before completion and updates the derived projection under
  the surrounding locked transaction.
- Controls: behavior-first RED/GREEN tests, public conflict matrices, migration acceptance, exact
  zero-write ledgers, full backend coverage, frontend gates, migration sync, and protected-path
  review all passed.
- Residual risk: PostgreSQL-specific approval races remain covered by the existing trusted harness
  and are among the 19 expected SQLite skips; this slice did not alter their lock ordering.
