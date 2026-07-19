# Database and Atomicity Proof

- Migration: `sfpcl_credit/loans/migrations/0003_repayment_repaymentsappostingobligation_and_more.py`.
- Global unique constraints: canonical bank reference and SHA-256 idempotency-key digest.
- Check constraints: positive receipt amount, bounded source/method/status values, pending allocation,
  required text, and complete pending/posted SAP evidence tuples.
- Singular links: receipt-to-obligation, obligation-to-task, receipt-to-capture audit, and posted
  obligation-to-posting audit.
- SQLite database proof: `DirectRepaymentPostingApiTests.test_database_rejects_nonpositive_receipts_and_duplicate_canonical_references`.
- PostgreSQL proof: `DirectRepaymentPostingPostgreSQLAcceptanceTests` has exactly two tests. Both
  same-key and same-canonical-reference races retain one receipt, obligation, task, and audit.
- Twice-run logs: `evidence/terminal-logs/postgresql-acceptance-run-1.log` and
  `postgresql-acceptance-run-2.log`; both record `Ran 2 tests`, `OK`, and `EXIT_CODE=0`.
