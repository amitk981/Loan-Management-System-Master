# Risk Assessment

Risk level: High

- Selected slice: 010C-principal-first-allocation
- Mode: normal_run
- Financial/data-integrity exposure: the slice changes principal, interest, total outstanding,
  installment paid amounts, loan status, and append-only ledger evidence.
- Primary controls: one atomic allocator transaction; receipt/account/schedule row locks; one-to-one
  allocation and ledger identities; non-negative, arithmetic, rule-version, and no-charge database
  constraints; immutable model/query interfaces; coherent 010B capture-audit reconciliation.
- Schedule controls: paid principal, interest, and charges are independently constrained not to
  exceed their corresponding due amounts.
- Idempotency/concurrency: exact replay returns retained truth without writes. The declared one-test,
  five-request PostgreSQL race is collected locally and must pass twice under independent validation.
- Policy risk: source docs do not define multi-installment ordering or a stored partial status. A-139
  records oldest-installment-first within principal then interest, retains partial rows as `pending`,
  and requires future governance confirmation without rewriting retained evidence.
- Excess/charges: no configured waterfall exists, so charges receive zero and the remainder is
  explicitly exceptional/unallocated. A zero allocated amount is representable without fabricating a
  financial credit.
- Regression controls: focused 010A/010B and Epic 009 opening-balance tests passed; capture and SAP
  evidence remain unchanged except for the receipt's allocation-status transition.
- Frontend risk: none; this slice changes no frontend files or visual contract.
- Residual risk requiring independent validation: real PostgreSQL lock behavior and the authoritative
  complete backend coverage gate.
