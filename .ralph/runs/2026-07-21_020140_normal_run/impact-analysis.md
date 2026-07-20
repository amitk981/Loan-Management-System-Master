# Impact Analysis

## Affected backend modules

- `monitoring`: reminder persistence, reminder engine, HTTP conflict/batch envelopes, migration, and
  public regression tests.
- `monitoring` DPD public owner: read-only consumption of retained first-unpaid, cutoff, and policy
  evidence; no DPD recalculation or mutation.
- `communications`: public dispatcher/template/job/status/evidence facade remains the provider seam;
  production changes here are only permitted if its existing public conflict contract is insufficient.

## Blast radius

- Existing quarter-end reminder creation and manual phone/electronic reminder endpoints.
- Electronic send idempotency, provider job uniqueness, delivery status projection, and audit trail.
- PostgreSQL concurrency behavior for quarter runs and competing sends.
- No frontend, cadence, default transition, provider adapter, or recipient-policy changes.

## Regression tests

- `test_reminder_queue_api.py`: calendar boundary/leap-year decision, advanced DPD pointer,
  execution-time repayment/resolution, exact/changed/cross-reminder keys, and mixed batch outcomes.
- `test_servicing_postgresql_acceptance.py`: exact five-test 010J2 class covering the closure contract.
- Focused existing DPD and communications tests: immutable DPD snapshots, dispatcher idempotency,
  delivery jobs, retries, channel contract, and worker behavior.
