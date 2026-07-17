# Review Packet: 2026-07-17_220706_repair

## Result
Repair complete pending independent validation

## Slice
009G3-post-transfer-aggregate-and-checklist-integrity-closure

## Failure diagnosis

The first real error in parallel coverage was `no such column:
disbursements.register_update_id`. The later `cannot pickle 'traceback' object` came from Django's
parallel runner while reporting that database error. `makemigrations --check --dry-run` independently
identified the same missing 0007 migration.

## Repair reviewed

- Added one disbursements migration for the already-preserved protected owner relation and amended
  aggregate constraint.
- Added a fail-closed data step that links only coherent singular 009G2 transfer/register/advice
  evidence and rejects non-success, incomplete, ambiguous, or changed legacy facts.
- Preserved APIs, public owners, frontend, permissions, dependencies, protected files, and the
  quarantined test/implementation diff.

## Verification

- RED: `makemigrations --check --dry-run` requested 0007 and exited 1.
- GREEN: migration sync reports `No changes detected`.
- GREEN: fresh test database applies 0007 and the protected-register regression passes.
- GREEN: the exact prior coverage-crashing initiation test passes.
- GREEN: all 11 transfer-success tests and Django check pass.

## Traceability

M08-FR-009 and data-model §34 require Loan Register truth to be part of successful-transfer
integrity. The migration makes the retained protected owner relation executable in the database and
refuses to backfill it from anything short of the exact existing evidence tuple.

## Recommended Next Action

Run full independent Ralph validation, including complete backend coverage and the declared twice-
run PostgreSQL acceptance. Commit only if every gate passes.
