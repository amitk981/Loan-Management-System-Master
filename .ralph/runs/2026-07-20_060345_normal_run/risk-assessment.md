# Risk Assessment

Risk level: High

- Selected slice: 010E3-servicing-financial-owner-and-replay-convergence
- Mode: normal_run
- Financial/data-integrity exposure: allocation replay, statement admission, effective-rate
  versioning/consumption, loan-rate projections, and mixed ledger reads.
- Main failure modes: mutable replay output, ambiguous subsidiary identity admission, truncated
  consumed rate periods, split loan/history truth, leaked uniqueness errors under races, and
  pagination drift.
- Controls implemented: append-only model/queryset guards, canonical activation/consumption owners,
  transaction/row locks, domain conflicts, frozen replay projections, symmetric ambiguity rejection,
  bounded database movement windows, deterministic ordering, and public synthetic builders.
- Historical values were not rewritten. No migration or dependency was added.
- Local evidence: 73 affected tests passed (7 PostgreSQL-only skips), focused RED/GREEN tests passed,
  Django check passed, and migration sync reported no changes.
- Residual risk: SQLite cannot prove PostgreSQL lock/uniqueness behavior. The declared five-test
  PostgreSQL class must pass twice in independent validation before merge.
- External effects: none; no deployment, network call, real communication, or real financial data.
- Manual review required: independent high-risk validation and PostgreSQL race gate.
