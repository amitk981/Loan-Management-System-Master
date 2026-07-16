# Risk Assessment

Risk level: High (standing owner approval; no veto is recorded).

## Financial and workflow risk

This slice creates the durable identity and immutable terms for a sanctioned loan. A forged or
stale source, duplicate number, premature balance, or unsafe replay could create false receivable
or disbursement truth. Controls are transaction-first locks, database uniqueness/amount constraints,
exact terminal-sanction coherence, frozen/current fact comparison, zero initial balances, one
append-only history tuple, and no readiness/disbursement/activation side effects.

## Authority and privacy risk

`finance.loan_account.create` remains Critical and deliberately ungranted to production roles under
A-121. The service reloads an active persisted actor, enforces the permission and application scope
before source lookup, and exposes only safe ids plus amount/type/rate/repayment. Borrower PAN,
Aadhaar, bank plaintext, legal/security payloads, document checksums/storage, SAP code plaintext,
and delivery capabilities are absent from responses and ledgers; focused secret scans cover success
surfaces and zero-write errors.

## Integrity and concurrency risk

Account/application/sanction and normalized account number are database-unique. Terms are one-to-one
and immutable; status history is append-only and freezes application/member/sanction/SAP/terms/
outcome provenance. Current legal selection rejects a newer invalid/replaced row instead of falling
back. SAP active/request truth is read through the public owner under `SELECT FOR UPDATE`.

The coding sandbox cannot access `/tmp/.s.PGSQL.5432`; the exact denial is retained in evidence and
is not represented as acceptance. The declared five-caller PostgreSQL class must pass twice in the
orchestrator's independent capability gate before commit/merge. SQLite collection skips that class
honestly.

## Residual risk

- Governance must assign A-121 before a production role can create accounts.
- Existing terminal approval rows without a frozen governed dispute-resolution term fail closed;
  upstream governance must provide that term rather than mapping unrelated conditions precedent.
- Later 009D+ slices must use the public loan owner and must not reinterpret `sanctioned` or zero
  balances as readiness/funding.
