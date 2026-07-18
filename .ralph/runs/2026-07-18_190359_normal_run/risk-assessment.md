# Risk Assessment

Risk level: High

- Selected slice: 009H8-communications-worker-runtime-and-crash-recovery-closure
- Mode: normal_run
- Standing approval: active; no owner veto is recorded.

## Material risks

- A worker can die around an external provider call, so duplicate borrower communication is the
  primary harm. The implementation keeps the H7 idempotency key at the provider seam, persists
  accepted evidence before local finalization, reuses that evidence after restart, and fences all
  local claim mutations. A process that truly dies cannot resume; a delayed expired process is
  rejected before provider entry and before acceptance/rejection persistence.
- Concurrent workers can claim or recover the same row. UUID claim fencing, database constraints,
  row-only `FOR UPDATE`, bounded recovery transactions, and twice-run PostgreSQL races retain one
  accepted provider identity and one terminal chain.
- A stale legacy-partial advice job could otherwise resend unverified history. Due/recovery selectors
  exclude H6 legacy provenance, mutate neither job nor outbox, and expose only safe operator-blocked
  evidence.
- Runtime/broker publication can fail after the request transaction commits. Robust on-commit
  publication prevents a false request rollback; the committed queued row remains reachable by the
  periodic task. Exhaustion retains one singular operator notification.
- Migration 0010 changes live job schema. Existing running rows receive expired fenced claims while
  ids, attempts, status, schedule, failure, provider, and timestamps remain unchanged; a migration
  regression proves the transition.

## Residual operational risk

Provider idempotency remains essential for the unavoidable process-death interval after an external
provider accepts but before local acceptance commits. Production must configure a real idempotent
email adapter and durable broker/result backend; repository defaults are deliberately inert
in-memory/manual values and cannot fabricate success. A-134 records the configurable five-minute
lease and 100-row batch defaults.

No money, loan status, UTR, bank evidence, frontend behavior, protected files, or source documents
were changed. No real personal/financial data or provider was used.
