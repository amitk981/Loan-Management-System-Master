# Risk Assessment

Risk level: High (standing approval; no veto)

- Selected slice: 006D2C-loan-limit-concurrency-and-boundary-regression
- Mode: normal_run
- Financial correctness: production calculation/formula/persistence code is unchanged. New tests
  exercise the existing public transaction boundary and compare full snapshot/audit/workflow
  outcomes.
- Database risk: no model or migration change. A PostgreSQL-only test settings module was added;
  default runtime/local settings remain SQLite and unchanged.
- Dependency risk: added one pre-approved pinned dependency, `psycopg[binary]==3.3.4`, solely to
  execute PostgreSQL integration tests. The offline sandbox did not install it, as required.
- Boundary risk: test-only AST analysis became broader. Positive fixtures and an allowed
  extra-method fixture reduce false positives from harmless interface refactors.
- Residual risk: the authoritative two-thread tests could not execute locally because the newly
  pinned driver is absent. SQLite explicitly skips them and is not treated as proof. Independent
  validation must install requirements, provision PostgreSQL, and run the exact command in
  `review-packet.md`; do not commit if that command fails.
- Rollback: remove the new test settings/dependency and test changes; no data rollback is needed.
- Protected/source files: untouched.
- Manual review required: yes, focused on PostgreSQL green output before orchestrator commit.
