# Risk Assessment

Risk level: High

- Selected slice: `010H2-interest-calculation-payment-and-replay-owner-closure`.
- Financial/data-integrity risk: annual invoices, monthly accruals, and capitalisation now share one
  segmented accounting decision. Incorrect date inclusivity, payment ownership, or replay behavior
  could alter borrower balances.
- Concurrency risk: invoice/accrual/capitalisation owners lock the loan account and recheck the
  idempotency owner after the lock. The declared five-test PostgreSQL class passed twice against
  separate real PostgreSQL test databases.
- Migration risk: one additive interest migration adds retained calculation/response evidence and
  payment, schedule, and hard-copy relations. Existing rows receive empty JSON/list defaults; no
  historical amount is rewritten or inferred.
- Provider risk: communication delivery remains an honest mutable provider projection, while the
  financial action's original response is immutable. Failed provider delivery cannot repeat money.
- Compatibility risk: external API shapes and routes are unchanged. Existing focused invoice,
  accrual, capitalisation, and loan-account read suites passed 44/44.
- Residual risk: unverifiable legacy rows keep empty newly-added evidence rather than receiving
  invented historical segments or responses. The orchestrator's complete coverage/migration gates
  remain authoritative.
- Protected/source/frontend files were not modified. No external communications were sent.
