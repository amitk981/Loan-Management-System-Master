# Review Packet: 2026-07-20_074651_repair

## Result
Ready for independent validation

## Slice
010F-interest-invoice-generation

## Recommended Next Action
Run the complete independent Ralph validation, especially the six-worker backend coverage gate. The
declared PostgreSQL race already passed twice in the failed candidate and must be revalidated by the
orchestrator before commit.

## Failure Diagnosis

- Exact independent symptom: six full-suite errors across credit ownership, statement ownership,
  and witness evidence migration tests.
- Tight reproducer: the three affected migration-test classes together produced `FAILED (errors=6)`.
- Root cause: both historical application projections enumerated migration leaves but did not exclude
  the newly added downstream `interest` leaf. That leaf's correct current-loan dependency caused the
  projected registry to outrun the intended historical schema. Credit `setUp()` then failed before
  teardown, leaving a partial schema that caused the remaining errors.

## Repair Review

- Added `interest` to the downstream-owner exclusions in
  `CreditAssessmentModelOwnershipMigrationTests` and `WitnessEvidenceMigrationTests`.
- No production code or migration was altered during repair; the quarantined 010F implementation was
  preserved byte-for-byte.
- The fix is aligned with the tests' existing design: configuration, legal, loans, SAP,
  disbursements, and communications were already excluded for the same historical-projection reason.

## Verification Evidence

- RED: `evidence/terminal-logs/migration-worker-order-red.log` — exact six tests, six errors.
- GREEN: `evidence/terminal-logs/migration-worker-order-green.log` — six tests pass, exit 0.
- Determinism: `evidence/terminal-logs/migration-worker-order-green-repeat.log` — second fresh run,
  six tests pass, exit 0.
- Preserved slice behavior: `evidence/terminal-logs/interest-invoice-focused-green.log` — all six
  010F API tests pass, exit 0.
- Static gates: `evidence/terminal-logs/backend-check.log` and
  `evidence/terminal-logs/migrations-sync.log` — both exit 0.

## Traceability and Independent Review Focus

- The source-backed invoice contract remains exactly as documented in the original candidate's
  review packet: backend-owned FY/rate/principal calculation, immutable evidence, configurable owner,
  duplicate safety, and document/communication issuance.
- Independent review should confirm the complete suite no longer depends on migration-test worker
  ordering and that no other historical projection admits `interest.0001` at a pre-loan/pre-rate
  boundary.
