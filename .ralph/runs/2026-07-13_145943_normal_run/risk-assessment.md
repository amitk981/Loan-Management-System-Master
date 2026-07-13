# Risk Assessment

Risk level: High

- Selected slice: `007D3-returned-approval-cycle-and-resubmission-closure`
- Mode: `normal_run`
- Standing approval: active; no owner veto exists.

## Material risks and controls

- **Approval authority leakage across cycles:** each action remains keyed to an immutable case;
  cycle N+1 starts with an empty action ledger, and tests prove cycle 1 is exact-equal after final
  cycle-2 approval.
- **Duplicate/open cycle race:** application -> appraisal -> case locking is retained; database
  constraints enforce unique application/cycle and one pending application cycle. The slice now
  declares `postgresql-five-race-acceptance` for trusted twice-run validation.
- **Stale review approving changed facts:** resubmission requires non-empty correction evidence
  after return and a later immutable Credit Manager review. No-op updates and missing fresh review
  are stable denials.
- **Historical fact drift:** enrichment freezes review facts per cycle; coherence refresh covers
  every case sharing an appraisal, and current/history read-scope matrices are tested.
- **Migration risk:** one additive migration backfills cycle 1, matched safe review identity, and
  frozen facts; migration isolation and reverse graph restoration are tested.
- **Local environment limitation:** the sandbox denied PostgreSQL Unix-socket access. This is not a
  product failure; the declared capability causes the orchestrator to run the race twice outside
  the sandbox and decide acceptance.

No protected files, source documents, external systems, real communications, or production data
were modified. The change is within the configured file/line/dependency/migration limits.
