# Ralph Handoff

## Last Run

2026-07-18_162512_normal_run

## Current Status

009H6 is complete pending independent validation. Communications migration 0008 now preserves only
provable post-0005 frozen provenance as `verified`; deterministic 0005 attempts are
`legacy_0005/legacy_partial`, while attempt-less or checksum-incoherent rows remain honestly
`ambiguous_legacy/legacy_partial`. Partial rows retain rendered/provider/receipt/Communication/
action/audit/workflow truth but clear the mutable template FK, every reconstructed source fact, and
checksum. Database constraints bind origin, status, and full-versus-null snapshot shape.

Current replay/finalization and portal/download truth require verified frozen provenance and reject
both legacy adapter identities with zero provider calls. Genuine legacy reversal refuses before
losing the origin marker; clean verified rows reverse/reapply exactly. RED/GREEN evidence, 41
impacted public tests, every migration fixture, Django check, migration sync, compile, and both
PostgreSQL five-caller methods in two final executions pass. Independent Standards review found no
production/test violation, and Spec re-review found no remaining fidelity issue.

## Next Run

Run 009H7 next, then 009H8 and 009I2 before 009J and 009K. H7/H8 now explicitly preserve and
exclude H6's provenance origins during generic-job migration and worker claim/recovery.
