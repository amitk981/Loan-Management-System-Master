# Risk Assessment

Risk level: High

- Selected slice: 009L5-epic-009-exact-selector-and-consumer-parity-closure
- Mode: normal_run
- Manual review required: yes; Ralph independent validation is authoritative.

## Material risks and controls

- **Existence disclosure through pagination:** lifecycle actor-role evidence, SAP completion digest,
  SAP send checksum, and CFC initiation-comment digest now participate in the database identity
  selector before count and offset. The retained four drift probes and a six-consecutive-drift page
  regression prove zero totals or stable pages rather than body-only suppression.
- **Cross-application SAP advancement:** the member portal now requires the canonical SAP decision's
  `loan_application_id` to equal the requested application. A retained reverse-consumer probe proves
  another application's completion cannot mark `sap_setup` complete.
- **Policy drift through duplicate validators:** locked single-row and bounded bulk lifecycle reads
  now call the same `_created_account_decision` implementation. Existing creation, readiness,
  initiation, authorisation, transfer, advice, and account-read tests exercise both call paths.
- **PostgreSQL digest support:** the CFC exact selector uses Django's SQL `SHA256`; migration
  `disbursements.0010_enable_pgcrypto_for_exact_selector` installs PostgreSQL `pgcrypto`
  idempotently and is a no-op-compatible migration on the local SQLite test database. Deployment
  must retain the normal database migration privilege to create extensions.
- **Performance:** exact filters remain database count/offset/limit queries; the four-row overscan
  was removed. Existing 1/21/101 Loan Account query ceilings and the long-drift regression are green.
  Ralph's full-suite/coverage gate remains the authoritative broad performance-regression signal.
- **No financial mutation change:** this slice changes read identity selection and one portal stage
  predicate only. It does not add posting authority, transfer behavior, money calculations, or
  Epic 010 behavior.

## Residual validation

- Runtime capability is `none`, so this agent did not run a live PostgreSQL acceptance lane. The
  migration smoke, Django check, migration-sync, 45 impacted tests, and 179 reverse-consumer tests
  are green; Ralph must still run the configured complete backend suite under coverage.
