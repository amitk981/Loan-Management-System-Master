# Risk Assessment

Risk level: High

- Selected slice: 010H-interest-capitalisation-after-30-april
- Mode: repair
- Standing approval: applicable; no matching owner revocation exists.
- Independent validation required: yes.

## Demonstrated failure and correction

- The independent PostgreSQL gate failed twice because the eligible-invoice queryset used an
  unrestricted `SELECT FOR UPDATE` while its `capitalisation_evidence__isnull` predicate introduced
  a nullable outer join. PostgreSQL correctly refused to lock the nullable side.
- The correction restricts the row lock to `InterestInvoice` itself with `of=("self",)`. The
  account remains locked first, the eligible source invoices remain locked, and no business rule,
  derived amount, transaction boundary, schema, or API contract changed.
- The exact declared PostgreSQL acceptance class now runs one test successfully and destroys its
  test database cleanly. This also confirms that the earlier lingering-session teardown error was
  secondary to worker requests aborting before connection cleanup.

## Financial and regression risk

- A too-broad relaxation could permit duplicate capitalisation. This repair does not remove the
  account or invoice locks; database uniqueness, post-account-lock idempotency recheck, and the
  atomic principal/ledger transaction remain unchanged.
- SQLite does not enforce PostgreSQL's nullable-join lock restriction, so the exact real-PostgreSQL
  contract is the decisive regression proof. Focused API tests additionally confirm the existing
  cutoff, money derivation, evidence, replay, permission, and rollback behavior remains green.
- No frontend, dependency, migration, protected-path, or source-document file changed in the repair.

## Residual risk

- Ralph's independent validation must still rerun the declared PostgreSQL contract twice and run
  the authoritative complete backend suite under coverage. The agent intentionally did not
  duplicate that complete-suite gate.
