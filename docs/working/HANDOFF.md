# Ralph Handoff

## Last Run
2026-07-11_032719_normal_run

## Current Status

004E2 is complete. New witnesses persist and expose the exact qualifying shareholding UUID and
verification-time folio, so later holding status/count/folio changes or new holdings cannot rewrite
the evidence. Legacy rows are linked only when one creation-audit folio resolves to exactly one
member shareholding; ambiguous, missing-audit, and no-match rows remain explicitly nullable.
Malformed JSON and non-object bodies now return `400 VALIDATION_ERROR` without witness/audit/
workflow writes. The named application/PAN-hash/Aadhaar-hash indexes each exist exactly once, and
witness list query/serialization composition is behind the application service seam.

006G3 received an additional concrete static/interface-test anchor. The remaining corrective order
is 006G3 -> 006H4 -> 006H3 -> 006X.

## Validation

TDD, API/migration/index, and configured gate logs are under
`.ralph/runs/2026-07-11_032719_normal_run/`. The full backend suite passed 394 tests with five
expected skips at 94% coverage; frontend build/typecheck/lint and 130 tests passed.

## Next Run

Run `006G3-sanction-handoff-dependency-and-evidence-ownership`, then 006H4, 006H3, and 006X in
dependency order. Witness verification history is accepted; sanction dependency ownership and the
current Workbench action UI remain unaccepted until their corrective slices pass.
