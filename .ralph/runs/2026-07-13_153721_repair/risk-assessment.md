# Risk Assessment

Risk level: High

- Selected slice: 007D3-returned-approval-cycle-and-resubmission-closure
- Mode: repair
- Repair scope: test organization only; no production, migration, API, permission, or frontend
  behavior changed during repair.
- Demonstrated failure: the protected PostgreSQL predicate requires exactly five selected races,
  while the selected classes discovered six after 007D3 added its returned-cycle race.
- Change: retained the returned-cycle race in `SanctionSubmissionConcurrencyTests` and moved the
  older initial-submission race, unchanged, into `InitialSanctionSubmissionConcurrencyTests`.
- Primary risk: accidentally dropping a concurrency proof from normal discovery or from the
  authoritative five-race selection.
- Mitigation: exact trusted selection passed twice with five tests; the moved legacy race passed
  separately on PostgreSQL; the full backend suite still discovers 628 tests and passes.
- Data/security impact: no real data, credentials, external calls, permission changes, or schema
  changes were introduced by the repair. PostgreSQL evidence omits credentials.
- Rollback: revert only the test-class split if the protected acceptance contract changes; do not
  revert the preserved 007D3 implementation.
- Independent review required: yes, through the Ralph full-gate revalidation before commit.
