# Ralph Handoff

## Last Run

2026-07-18_184623_repair

## Current Status

009H7 is complete pending independent repair validation. Generic communication and disbursement
advice now cross the source-shaped communications dispatcher and one retained generic job identity.
Both HTTP sends require a bounded explicit `Idempotency-Key`, bind it to exact
object/payload/actor truth, and return zero-write exact replay while rejecting changed, cross-actor,
or cross-object use.

Migration 0009 preserves existing H5 job ids/history and excludes H6 legacy-partial provenance.
The disbursement owner no longer imports/registers the process coordinator. Manual/no-provider mode
cannot fabricate provider acceptance; Fake/configured adapters retain provider truth, and generic
acceptance is frozen before final Communication mutation. Fifty-seven focused tests, six H6
migration regressions, required backend checks, frontend gates, and all six PostgreSQL five-caller
races in two final executions pass.

The first independent complete-coverage run found one stale pre-H7 notification integration test:
it called the generic send endpoint without the now-required key and expected HTTP 200. Repair
`2026-07-18_184623_repair` reproduced the exact 400, supplied one stable explicit key in that test,
and passed the exact test plus all 14 notification/generic-communications API tests. Production
dispatcher code and its fail-closed missing-key contract were not changed.

## Next Run

Run 009H8 next, then 009I2 before 009J and 009K. H8 is already sharpened to register the Celery
runtime, on-commit scheduling, leases, stale-running recovery, accepted-evidence replay, and H6
legacy exclusion; I2 is already sharpened for exact owner timestamps and real-browser evidence.
