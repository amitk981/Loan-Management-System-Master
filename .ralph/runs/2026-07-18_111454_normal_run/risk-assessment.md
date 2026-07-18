# Risk Assessment

Risk level: High

- Selected slice: 009G5-legal-migration-state-guard-closure
- Mode: normal_run
- Standing approval: active; no owner veto exists.

## Risk factors

- The guard protects migration-state ownership for the legal checklist used in the disbursement
  completion path. A false negative could allow a future downstream migration to change legal
  state; a false positive could block an otherwise safe migration.
- The retained exception covers applied historical operations and therefore must not be widened by
  filename, class-name, inheritance, helper, or target-model tricks.
- The synthetic-source test adapter executes only test-supplied migration source. Repository checks
  load the real Django migration graph and do not execute file text through that adapter.

## Mitigations and residual risk

- The implementation compares Django `ProjectState` before and after every operation rather than
  inferring behavior from source spelling. The exception additionally binds path, module, class,
  position, sole changed model, and exact constraint delta.
- The architecture-review bypass failed first. Imported, inherited, helper, renamed, sibling,
  changed-target, legal-owner, and database-only variants are retained as executable tests.
- The complete 009G4 row/schema forward-reverse-reapply manifest and five adjacent migration-owner
  modules pass. Django reports no model drift, and legal 0015 still emits no SQL.
- No migration, model, production workflow, API, frontend, dependency, or protected path changed.
  Residual risk is limited to an unusual future Django operation whose `state_forwards` behavior is
  nondeterministic; such an operation would itself violate normal migration design expectations.
