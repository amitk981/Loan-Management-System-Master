# Review Packet: 2026-07-20_153054_normal_run

## Result
Ready for independent validation

## Slice
010I-dpd-calculation-and-monitoring-buckets

## Implementation Summary

- Added the `monitoring.modules.dpd_monitoring` owner and three source-defined monitoring endpoints.
- Added immutable DPD snapshots, effective optional operational schemes, database uniqueness,
  current-pointer advancement, per-calculation audit evidence, and bounded portfolio-run evidence.
- Reconstructed historical paid amounts from posted allocation/reversal ledger dates and retained
  SOP and optional standard classifications independently.
- Granted source actors Credit Manager, CFO, and Accounts Head the exact DPD read permission; write
  authority remains the existing Credit Manager calculation grant.

## Traceability

- The source doc says DPD is `as_of_date - earliest_unpaid_due_date` and must use due dates plus the
  repayment ledger (`data-model.md` §35.4; `functional-spec.md` M11-FR-002); the code calculates from
  schedule rows and immutable allocation/reversal ledger dates, verified by
  `DpdPaymentTimingApiTests.test_later_posted_repayment_does_not_reduce_earlier_snapshot`.
- The source doc says SOP buckets remain Current/1–2/2–3/>3 years while 0–30/31–60/61–90/>90 is
  optional and separate (`functional-spec.md` M11-FR-003/004); the code resolves separate snapshot
  fields and an effective optional scheme, verified by
  `DpdMonitoringApiTests.test_calendar_and_configured_operational_bucket_boundaries`.
- The source API defines single calculate/read and bulk calculate (§34.1–34.2); the code exposes those
  exact paths with standard envelopes and strict inputs, verified by the eight-test focused API file.
- The slice requires stable same-date concurrency; the declared
  `DpdSnapshotPostgreSQLAcceptanceTests` passed twice against PostgreSQL with one snapshot, audit,
  and pointer.

## Verification Evidence

- RED/GREEN tracer: `evidence/terminal-logs/dpd-tracer-red.log` and `dpd-tracer-green.log`.
- RED/GREEN historical timing, permission, portfolio, replay, bucket, and immutability cycles:
  `evidence/terminal-logs/dpd-*-red.log` / corresponding `dpd-*-green.log`.
- Consolidated focused suite: `evidence/terminal-logs/dpd-focused-green.log` — 8 tests, OK.
- PostgreSQL contention: `dpd-postgresql-race-green.log` and
  `dpd-postgresql-race-green-2.log` — one test each, OK.
- Reverse consumers: `dpd-reverse-consumers-green.log` — 010A/010C/010H selectors, 3 tests, OK.
- Permission seed: `dpd-permission-seed-green.log` — 17 tests, OK.
- Django and migration sync: `backend-check-green.log` and `migrations-check-green.log`.
- Response examples: `evidence/dpd-api-examples.md`.

## Review Notes

- No frontend or styling files changed; 010M remains the staff UI owner.
- No reminder, default, extension, MIS, or loan workflow transition was added.
- No protected file, source document, package dependency, or external service was changed.
- The complete backend suite/coverage and full frontend gates were deliberately not run locally;
  the Ralph orchestrator owns those authoritative gates.

## Recommended Next Action
Run independent Ralph validation, including the declared PostgreSQL acceptance twice and the full
backend coverage gate.
