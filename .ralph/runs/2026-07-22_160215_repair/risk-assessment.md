# Risk Assessment

Risk level: High (inherited from slice 011E)

- Selected slice: 011E-recovery-decision-approval
- Mode: repair
- Demonstrated validation domain: complete backend coverage / historical migration-state isolation.
- Repair surface: two existing migration tests; no production logic, schema, API, permission, or
  source-contract change.

## Failure mechanism

Adding `recovery.0001` introduced a new graph leaf. Two historical migration tests derived their
old app registries from all leaf nodes except a hand-maintained set of known downstream owners. The
new recovery leaf depends on current approvals/defaults and therefore pulled current `credit` and
`applications` model states into projections whose physical schemas had been migrated backward.
That produced the missing historical credit model and later Witness-column mismatch.

## Controls and residual risk

- Both failures have deterministic focused RED/GREEN evidence.
- Django check and migration-sync probes pass.
- The exact six-worker complete suite passes all 1,619 tests at 90% coverage, above the 85% floor.
- Repair changes only add `recovery` to the two downstream-leaf exclusion sets.
- Residual risk: these historical tests use explicit downstream-owner allowlists, so a future app
  whose migrations depend on current `applications`/`credit` state may require the same isolation
  update. Current recovery dependencies were audited; SAP ownership state is not in their forward
  dependency plan.
- Independent High-risk validation remains required before commit/merge.
