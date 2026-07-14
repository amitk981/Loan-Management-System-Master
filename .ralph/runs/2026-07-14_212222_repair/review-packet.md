# Review Packet: 2026-07-14_212222_repair

## Result

Repair complete; ready for independent orchestrator revalidation.

## Demonstrated Failure and Fix

The normal run failed only `limits.max_lines_changed`: 2,965 lines against 2,000. The exact local
validator loop is now green at 1,994 lines. The repair removed duplicated migration state and made
the security public module bind the retained legal evidence engine, avoiding double-counted file
relocation while preserving the implemented contracts.

## Traceability

- Source architecture says the retained security package/PoA tables and §28 routes belong to the
  security boundary. Runtime app ownership, models, routes, request contract, package policy, and
  public PoA binding live under `security_instruments`; the legal evidence engine imports no
  security policy. Verified by `SecurityInstrumentBoundaryTests` and migration-state regression.
- Source permissions/lifecycle say Compliance prepares and a distinct active Company Secretary
  checks exact facts. The code preserves current-maker handoff, effective secondary roles, exact-
  draft activation, terminal replay/downgrade behavior, and durable §6.3 action identity. Verified
  by `PowerOfAttorneyApiTests`.
- Source integrity rules require retained tables and atomic terminal evidence. The migration remains
  state-only; linked signature/stamp/notary mutations and downgrade races remain fail-closed.
  Verified by migration sync, the focused suite, and both PostgreSQL race tests run twice.

## Gate Evidence

- Exact diff limit: 1,994 / 2,000, green.
- Focused boundary/PoA: 11 tests green on SQLite (two PostgreSQL-only skips).
- PostgreSQL: two PoA concurrency tests green twice.
- Backend: Django check green; no migration drift; 814 tests green, 32 expected skips, 93% coverage.
- Frontend: build, typecheck, lint, and 293 tests green.
- Protected paths: no changes. No `[DEBUG-*]` instrumentation remains.

## Recommended Next Action

Run full independent repair validation. If green, commit/merge/push through the orchestrator only;
then run 008H followed by 008I.
