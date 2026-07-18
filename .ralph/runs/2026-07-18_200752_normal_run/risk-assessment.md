# Risk Assessment

Risk level: High (change-request classification); incremental implementation risk is Low.

- Selected slice: CR-011-github-ci-migration-test-schema-isolation
- Mode: normal_run
- Standing approval: active; no owner veto is recorded.

## Material risks

- Migration tests mutate a worker-wide schema. If cleanup is missing, later tests can execute current
  model code against old tables. The leaking approvals class now migrates all apps to the migration
  graph's current leaf nodes before its transaction-test cleanup completes.
- A communications test can be preceded by any migration-changing class in a parallel worker. It
  now explicitly migrates to current leaves during setup before constructing its current-model
  disbursement/approval fixture, and retains its existing leaf restoration during cleanup.
- Leaf migration setup/cleanup adds focused test runtime. This is preferable to order-dependent
  worker state and is restricted to the two affected migration classes.

## Residual validation risk

The local four-worker run could not reach test assertions because spawned macOS child processes
requested x86_64 while the mandated Ralph virtualenv contains an arm64 CFFI binary. Both serial
orders and the complete 16-class cleanup audit pass. The orchestrator/GitHub four-worker environment
must provide authoritative parallel acceptance and full coverage.

No production migration, model, service, API, endpoint, dependency, frontend behavior, protected
file, source document, business rule, money state, or personal/financial fixture changed.
