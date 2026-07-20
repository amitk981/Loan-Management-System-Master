# Final Summary

Result: Ready for independent validation

Implemented CR-014's server-owned current-date rate finalizer.

- Removed the caller-controlled explicit-date projection mutation seam.
- Added immutable account/version publication decisions with global idempotency, actor/role, audit,
  replay, and PostgreSQL uniqueness evidence.
- Kept Loan Account mutation behind a loan-owned facade; automated publication is attributed to the
  system, while manual publication enforces management permission and account scope.
- Added bounded portfolio publication through a Celery callable and list/detail invocation without
  inventing a scheduler cadence.
- Added deterministic stale-scalar repair from retained immutable evidence and a JSON-serializable
  Celery result.
- Kept stale-but-valid accounts in collection counts and bulk-refreshed selected rows before
  serialization, preserving query ceilings.
- Added the exact five-test declared PostgreSQL class plus permanent early-date, replay, matrix,
  runtime, read, and reverse-consumer regressions.
- Added additive migration `configurations.0008_current_rate_projection_decision`.

Local focused tests, Django check, migration sync, and the Loan Account read module passed. The local
connection is SQLite, so PostgreSQL-only tests were collected and skipped; Ralph's declared
twice-run PostgreSQL acceptance is still required and is not represented as locally proven.
