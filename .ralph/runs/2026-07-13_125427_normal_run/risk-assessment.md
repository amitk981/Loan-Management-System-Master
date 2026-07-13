# Risk Assessment

Risk level: High.

- Selected slice: 007D-approval-action-api-approve-reject-return
- Mode: normal_run
- Financial/authority impact: final joint approval creates the unique sanction decision and changes
  the application workflow state. Mitigations are immutable case authority snapshots, action-level
  permission and object scope, optimistic versioning, database uniqueness, deterministic lock
  order, atomic writes, and attributable audit/workflow evidence.
- Concurrency: application/appraisal/case rows are locked in that order and sanction decisions are
  unique by both application and case. Routine SQLite gates cannot exercise PostgreSQL lock races;
  the slice declares no PostgreSQL runtime capability, so the retained proof is lock/constraint
  design plus stale/duplicate exact-ledger tests.
- Source gap: A-079 keeps numeric interest/penal rates, repayment date, charges, and conditions
  nullable/empty rather than inventing financial facts absent from the reviewed appraisal.
- Residual risk: 007E must add conflict exclusion at the pre-insert hook; 007F/007H own exception
  and sanction register rows. Standing approval is active and no veto exists.
