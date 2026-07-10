# Risk Assessment

Risk level: High

- Selected slice: `006F-credit-manager-review`; standing owner approval applies and no veto exists.
- The slice changes a credit decision transition, role/object authorization, maker-checker, stored
  reviewer evidence, and audit/workflow persistence. Incorrect behavior could permit unauthorized
  progression or erase a return reason.
- Mitigations: dedicated action endpoint; independent review permission; Credit Manager domain
  scope; preparer/reviewer separation; strict state and verified-provenance guards; row locking;
  atomic appraisal/audit/workflow writes; metadata-only evidence; no sanction or rejection action.
- Data change is one additive migration with nullable/blank-safe defaults. No existing columns or
  rows are destructively rewritten.
- Regression proof covers reviewed/returned cycles, revision/resubmission, invalid/repeated states,
  permissions, scope, maker-checker, provenance, frozen assessment facts, redaction, and rollback.
- Residual risk: concurrent review is proven through `select_for_update` semantics and state guards
  but not by a separate PostgreSQL competing-transaction test in this slice. The existing full
  PostgreSQL concurrency gate remains documented for calculator changes; 006F adds no calculation.
- No frontend, external communication, deployment, financial calculation, or protected file was
  changed.
