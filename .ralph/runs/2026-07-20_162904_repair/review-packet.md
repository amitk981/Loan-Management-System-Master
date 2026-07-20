# Review Packet: 2026-07-20_162904_repair

## Result
Ready for independent validation

## Slice

010I-dpd-calculation-and-monitoring-buckets

## Repair Scope

Preserved the quarantined 010I implementation and repaired only the five migration-test errors from
the prior independent backend coverage gate.

## Diagnosis

- Exact reproducer:
  `sfpcl_credit.tests.test_witness_evidence_migration.WitnessEvidenceMigrationTests.test_backfill_only_links_unambiguous_audited_shareholding_evidence`.
- RED signal: `evidence/terminal-logs/witness-schema-probe.log` records
  `OperationalError: table witnesses has no column named verification_folio_number`, one error, and
  `Exit code: 1`.
- Root cause: the newly installed `monitoring.0001_initial` leaf depends on the current loans graph.
  The credit-ownership and witness-evidence migration tests projected all migration leaves except a
  fixed downstream-owner set. Because `monitoring` was absent from that set, their historical ORM
  projections reintroduced later `applications` models over tables explicitly reversed to older
  migrations.

## Repair

- Added `monitoring` to the downstream-owner exclusions in
  `test_credit_model_ownership_migration.py` and `test_witness_evidence_migration.py`.
- Updated the adjacent comments so the test seam documents why the exclusion is required.
- No production code, migration, API contract, permission, or DPD business behavior changed during
  repair.

## Verification Evidence

- `evidence/terminal-logs/migration-state-green.log`: the exact two modules containing all five prior
  errors pass together (`Ran 5 tests`, `OK`, `Exit code: 0`).
- `evidence/terminal-logs/witness-schema-green.log`: the minimal reproducer passes in isolation
  (`Ran 1 test`, `OK`, `Exit code: 0`).
- `evidence/terminal-logs/dpd-focused-green.log`: all eight selected-slice API/business tests pass.
- `evidence/terminal-logs/backend-check-green.log`: Django system check passes.
- `evidence/terminal-logs/migrations-check-green.log`: no model/migration drift.
- `git diff --check` passed with no whitespace errors; no `[DEBUG-*]` instrumentation remains.

## Source and Slice Traceability

- The slice and Epic 010 digest require deterministic DPD snapshots derived from schedule/ledger
  truth while preserving historical evidence. The original implementation and its focused tests are
  unchanged by this repair; the eight-test DPD suite remains green.
- The repair restores the authoritative complete-suite path without weakening historical migration
  assertions or modifying the source-defined DPD behavior.

## Independent Validation Boundary

The orchestrator must rerun the complete configured backend coverage suite and all other declared
gates before any commit. This repair run intentionally did not duplicate that full suite locally.
