# Risk Assessment

Risk level: High

- Selected slice: `010D-bank-statement-matching-unmatched-receipts`
- Mode: `normal_run`
- Financial/data-integrity exposure: statement lines can become evidence linked to receipts, but the
  slice has no interface that creates allocations, changes account/schedule/ledger balances, or
  marks SAP posted. Reverse-consumer tests snapshot those owners around matching.
- Provenance/privacy controls: retained CSV files use the existing restricted document storage seam;
  imports retain checksum, uploader, bank-account label, line/date/amount/reference facts, safe
  statuses, and timestamps. Queue/API/audit projections omit raw narration, raw references, file
  bytes, and manual reason text.
- Match controls: automatic matching requires singular exact UTR, amount, transaction date,
  canonical loan account, and narration containing account/application/borrower identity. Missing,
  malformed, mismatched, or already-consumed evidence remains unmatched/exceptional.
- Manual controls: a chosen receipt and nonblank reason are mandatory; line/receipt rows lock in one
  transaction; one-to-one/unique database fields prevent either counterpart from being consumed
  twice; manual decisions remain `manual_match_exception` with allocation still `pending`.
- Idempotency controls: key/body replay and same account/file checksum reuse one import; changed key
  reuse conflicts. A unique account/checksum constraint and one-to-one source document backstop the
  service checks.
- Authority controls: separate read/import/match permissions require one source-authorized Credit,
  Accounts, or Treasury role. Credit manual match scope hides non-serviceable receipt accounts.
- Policy assumptions: A-140 records the source-silent technical permission/status names. A-141
  records that the normalized SFPCL bank-account label is provenance only until governance supplies
  a collection-account registry; it never proves ownership or drives money movement.
- Existing storage-seam residual risk: document bytes are written before the database transaction
  commits. A database failure after storage can leave an unreferenced local object even though all
  database statement/document facts roll back. No duplicate financial or reconciliation truth is
  created; lifecycle cleanup remains the central storage owner's concern.
- Frontend risk: none; this slice changes no frontend files or visual contract.
- Residual risk requiring independent validation: the declared one-test PostgreSQL contention class
  collected but skipped locally under SQLite. Ralph must run it twice on PostgreSQL, then run the
  authoritative complete backend coverage, migration, protected-path, and diff gates.
