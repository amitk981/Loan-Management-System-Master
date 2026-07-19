# Execution Plan

Selected slice: 009L6-epic-009-owner-selector-equivalence-and-matrix-closure

## Repair Boundary

Preserve the quarantined 009L6 implementation and repair only the independently demonstrated
full-suite regression: historical migration-state `AuditLog` writers omit the new selector
manifest columns, while migration `identity.0004` created those columns as non-null without a
persistent database default.

## Plan

1. Reproduce one named full-suite error with the exact focused Django test label and retain the
   red output under this repair run's `evidence/terminal-logs/` directory.
2. Compare the current `AuditLog` model/migration field contract with historical migration-state
   inserts and test the smallest compatibility fix that preserves non-null manifest storage.
3. Re-run the focused reproducer, the other four named failures, migration synchronization, and
   the slice-owned selector/manifest tests using the orchestrator-managed Python interpreter.
4. Inspect targeted diff/stat output, record repair risk and traceability, and leave the review
   packet exactly `Ready for independent validation`; Ralph retains ownership of full-suite
   validation, changed-files/state/status bookkeeping, and commit/merge/push.

## Expected Files

- `sfpcl_credit/identity/models.py`
- `sfpcl_credit/identity/migrations/0004_auditlog_selector_manifest_sha256.py`
- `.ralph/runs/2026-07-19_151614_repair/**`

## Completion Note

The focused reproducer failed before the repair and passed afterwards. All five named independent
coverage errors then passed together; migration sync, Django checks, owner-selector tests, and the
pgcrypto ownership tests are green. Full-suite and PostgreSQL acceptance remain delegated to
Ralph's independent validator as required.
