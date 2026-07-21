# Risk Assessment

Risk: High. This correction changes financial classification, current reminder delivery authority,
historical reporting scope, and database mutation behavior.

- Financial integrity: capitalised interest is consumed only when its immutable ledger date is on or
  before the DPD as-of date; repayment/reversal behavior remains in the existing owner.
- Data integrity: one migration makes DPD reparenting and approved policy mutation fail at the
  database boundary; model/queryset guards cover ordinary adapters.
- Authorization: generation, submission, and review replays now traverse current report scope, and
  review replay additionally rechecks the exact submitted CFO.
- Delivery: final serviceability consumes locked current schedule truth before provider execution;
  no external provider was called by this run.
- Residual: the exact PostgreSQL five-test class must run twice in independent validation. Local
  SQLite proves behavior but cannot substitute for database race/trigger acceptance.
