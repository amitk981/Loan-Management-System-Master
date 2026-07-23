# Execution Plan — 011L Section 186 and NBFC Test Trackers

## Scope

Implement only the backend models, migration, domain modules, create/read/review APIs, permissions,
audit/evidence snapshots, quarterly compliance-task linkage, and tests declared by slice 011L.
Frontend wiring and unrelated compliance work are excluded.

## Permission Check

- Product edits are restricted to `sfpcl_credit/**`, which is allowed by `.ralph/permissions.json`.
- Run evidence is restricted to `.ralph/runs/2026-07-23_044808_normal_run/**`, which is allowed.
- `docs/working/API_CONTRACTS.md` and `docs/working/ASSUMPTIONS.md` may be updated only if the
  implementation discovers a contract delta or a source-silent decision.
- Protected paths, orchestrator-owned bookkeeping, slice status, and `docs/source/**` will not be
  edited.

## Behaviour-First Sequence

1. Inspect the existing 011K compliance public interfaces, models, permissions, routes, evidence,
   audit, and test conventions.
2. RED→GREEN: Section 186 public module calculation and boundary behaviour using Decimal values.
3. RED→GREEN: NBFC ratio, strict 50% trigger, one-ratio warning, configurable early-warning, and
   denominator validation behaviour.
4. RED→GREEN: period-unique persistence, frozen input/output snapshots, evidence/task ownership,
   exact replay, changed replay conflict, and review maker-checker behaviour.
5. RED→GREEN: create/read/review API envelopes, permissions, rejected caller-derived fields,
   evidence scope, denied-access audit, and reverse-consumer behaviour.
6. Add the single schema migration and the exact PostgreSQL concurrent-create acceptance test.
7. Run focused backend tests after each cycle, then Django check and migration-sync checks. Do not run
   the complete backend suite or coverage locally; Ralph validation owns the authoritative lane.
8. Inspect targeted diff/statistics, run static Decimal/no-float checks, and save terminal evidence,
   risk assessment, review packet, and final summary.

## Required Evidence

- One retained failing test output before implementation and matching green output after each
  behaviour increment.
- Focused service/API/permission/audit/reverse-consumer results.
- Migration sync and exact PostgreSQL race-test label/count evidence where locally available.
- Source-to-code-to-test traceability and a final review result of exactly
  `Ready for independent validation`.
