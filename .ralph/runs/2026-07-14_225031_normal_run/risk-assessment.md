# Risk Assessment

Risk: High.

This slice changes protected BO-account handling, legal-evidence consumption, critical-role
authority, maker/checker transitions, and database concurrency. Exposure is limited by masked
ordinary reads, an explicit separately audited reveal permission, authenticated sealed values,
one package-owned row, package-row locking, bounded/check-constrained states, unique PSN, and
PostgreSQL race acceptance executed twice.

Terminal acceptance requires a distinct active Company Secretary and freezes same-application
current-renderer evidence. Invocation/unpledge timestamps are database-constrained null. The flow
does not alter share balances, file access, checklist completion, package readiness, disbursement,
or loan-account state. The sealed-token construction is repository-local cryptography pending a
future managed AEAD/KMS owner; A-115 records that limitation and its rotation/versioning boundary.

No protected file, `docs/source`, frontend surface, external system, or git metadata was changed.
The owner standing approval applies and no revocation was found.
