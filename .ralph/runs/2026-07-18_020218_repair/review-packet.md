# Review Packet: 2026-07-18_020218_repair

## Result
Ready for independent validation

## Slice
009H3A-communications-advice-persistence-and-provider-identity

## Demonstrated Failure

The prior run's full parallel coverage failed five retained migration tests. The required
communications 0004 dependency on disbursements 0007 made communications a downstream leaf of
current application and credit migrations. Two historical test projections did not exclude that
new downstream owner, so their app registries expected current fields/models against intentionally
reversed schemas.

## Repair Review

- Preserved the quarantined 009H3A production implementation and migration unchanged.
- Added `communications` to the downstream-owner exclusion in the credit model-ownership and
  witness-evidence historical migration projections.
- Reproduced the exact missing `witnesses.verification_folio_number` failure with the new owner
  migration test immediately followed by the retained witness test, then proved the same order
  green after repair.
- Rechecked 009H3B and 009G4. Both already contain concrete fields/evidence, owner boundaries, role
  and endpoint rules, migration constraints, and executable tests; no sharpening edit was needed.

## Verification

- Exact two-test order repro: RED before repair, GREEN after repair (2 tests in 32.443s).
- All implicated migration modules: 6 tests pass in 170.252s.
- Advice foundation and retained public API: 23 tests pass; 2 PostgreSQL-only tests skip locally.
- Django check reports no issues; migration sync reports no changes; `git diff --check` passes.
- No debug instrumentation or protected-path edit was introduced. Complete parallel coverage remains
  the orchestrator's authoritative independent gate.

## Traceability

009H3A requires communications 0004 to depend on the current disbursements migration while
preserving historical owner-transfer proof. The code does exactly that. The repair makes retained
historical tests project the pre-migration application/credit state by excluding the newly
downstream communications leaf, verified by the ordered repro and all six migration tests.

## Recommended Next Action
Run complete independent Ralph validation. If green, commit 009H3A and execute 009H3B next.
