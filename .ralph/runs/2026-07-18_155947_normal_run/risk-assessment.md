# Risk Assessment

Risk level: High

- Selected slice: 009G6-legal-migration-exception-fingerprint-closure
- Mode: normal_run
- Standing approval: active; no owner veto exists.
- Database impact: none. No migration, model, schema, constraint, table, row, or identifier changed.
- Runtime/API impact: none. The only production change is the executable repository migration-state
  ownership guard.

## Material Risks

- A false negative could permit a future cross-owner migration to alter legal checklist state under
  a retained historical identity.
- A false positive could make repository validation reject the genuine applied disbursements 0005
  history or a legal-owned future migration.
- Django's normal `ProjectState.clone()` shallow-copies nested model options; an in-place constraint
  append can otherwise mutate both before and after snapshots and erase the observed delta.

## Controls and Residual Risk

- The guard uses a deep pre-operation snapshot, exact path/module/class/index identity, exactly one
  changed model, exact retained constraint serialization, and a canonical complete model-state
  comparison after omitting only the named transition.
- Real operations 0-3 pass. A 24-case matrix rejects field, constraint, index, option, base, and
  manager drift across both remove and both add identities; another-model and sibling-operation
  rejection remain covered.
- Forward/reverse/reapply manifests preserve exact rows and physical schema; legal 0015 remains
  zero-operation/zero-SQL. Django check, migration sync, compilation, and 20 focused tests pass.
- Residual risk is Low after the independent full-suite/coverage gate. Commit, merge, and push remain
  delegated to the Ralph orchestrator.
