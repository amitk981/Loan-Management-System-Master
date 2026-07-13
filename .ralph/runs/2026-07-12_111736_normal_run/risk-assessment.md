# Risk Assessment

Risk level: High

- Selected slice: 006Z-produce-supply-history-persistence
- Mode: normal_run
- Financial eligibility behavior changed from a manually verified member-profile shortcut to
  persisted supply evidence. Incorrect continuity, verification, or portal scoping could alter a
  credit decision or expose another member's records.
- One non-destructive migration creates `produce_supply_records`; no existing column or row is
  rewritten. Production PostgreSQL remains the target while routine tests use SQLite.
- Controls: source-named permission codes, maker-checker denial, optimistic versions with row
  locking, immutable verification actor/time, narrow audit/history projections, PortalAccount-only
  scope, and no portal mutation action.
- Regression controls: verified/unverified/absent/discontinuous eligibility tests; maker,
  permission, stale-write, own-scope, existing credit-flow, seed, and frontend display tests.
- Residual risk: source documents do not define fiscal-year string normalization beyond the
  documented `varchar(20)` field. Eligibility accepts only canonical `YYYY-YY` continuity; other
  values remain visible but do not silently qualify.
- Standing approval applies and no owner veto exists.
