# Risk Assessment

Risk level: High

- Selected slice: 006Z9-active-member-authority-and-decision-contract-closure
- Mode: normal_run
- Authorization behavior changed at a shared member-domain seam. Explicit global scopes are limited
  to member read, active-status verification, and identity-change approval; member update remains
  owner-scoped. The choice is recorded as A-072 for later assignment governance.
- Verification changes are transactional and reject before status, effective history, audit, or
  workflow writes. Public tests cover role-provenance parity, decision mismatch, and evidence-maker
  denial; the full backend suite and coverage gate pass.
- No schema, migration, dependency, frontend, source, protected, or design-system file changed.
- Residual risk: the source has no persisted member team/assignment model. Future governance may
  narrow the explicit global permissions, but must not restore role-code or system-role bypasses.
