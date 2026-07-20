# Risk Assessment

Risk level: High

- Selected slice: 010H-interest-capitalisation-after-30-april
- Mode: normal_run
- Standing approval: applicable; no owner veto was found for this selected slice.
- Independent validation required: yes.

## Financial and data-integrity risks

- A duplicate or raced request could otherwise increase principal twice. The implementation locks
  the scoped account and invoice/accrual truth, uniquely constrains `(loan_account, financial_year)`
  and the idempotency digest, rechecks exact replay after the account lock, and appends one immutable
  capitalisation ledger row.
- Caller-selected money could corrupt principal. The final API accepts only FY/date/key and rejects
  unpaid/principal/rate inputs; unpaid interest is derived from issued, uncapitalised invoice truth.
- A partial notification setup could leave money moved without required borrower evidence. Email
  snapshot/job, hard-copy PDF, audit, capitalisation, account update, invoice links, and ledger row
  are created inside one database transaction. Provider execution remains asynchronous and its
  queued/retrying/sent/failed state is reported honestly; replay after failed delivery does not move
  principal again.
- Historical calculations could be rewritten. Invoice and accrual models remain immutable; the new
  capitalisation stores their rate/calculation/accrual provenance and links source invoices through
  append-only evidence.
- Existing account reads previously excluded any active balance different from initial disbursement.
  The 010A reverse consumer now admits only transfer-backed serviceable accounts whose total equals
  principal plus interest plus charges, so valid capitalised balances are visible without admitting
  incoherent account rows.

## Migration and runtime risks

- One additive interest migration creates three tables, one date index, unique loan/FY and
  idempotency constraints, positive/arithmetic checks, and immutable application-level guards.
- The declared PostgreSQL race class collects exactly one test locally and is intentionally skipped
  under SQLite. Ralph's independent PostgreSQL gate must run it twice and remains the authoritative
  contention proof.
- The complete backend coverage suite is intentionally deferred to the orchestrator per AFK policy.
  No frontend files or dependencies changed.

## Residual risk

- Local storage writes occur through the existing document owner and database provenance contract;
  provider delivery remains retryable external work rather than part of the financial transaction.
- Full-suite/coverage and real-PostgreSQL results are pending independent validation. Focused
  contract, migration, reverse-consumer, and communication tests are green.
