# Risk Assessment

Risk level: Medium (slice-declared); repair delta is test-only and limited to the failed trusted
PostgreSQL acceptance domain.

- Selected slice: `011J-archive-record-and-retention`
- Mode: same-worktree `repair`
- Failure cause: the PostgreSQL race test asserted that the loan had one status-history row in
  total. The retained fixture correctly has two before archive: account creation and financial
  close. This made a correct archive race fail after all archive uniqueness checks had passed.
- Repair: snapshot the append-only loan-status history IDs before the race and assert that archive
  leaves the exact set unchanged. The test still independently requires one archive manifest, one
  completed archive requirement, one terminal archive workflow event, and one creation audit.
- Product/schema/API impact: none in the repair delta. The existing candidate is preserved.
- Concurrency: the exact five-racer PostgreSQL class passed twice against separate test databases,
  each discovering and running exactly one test.
- Environment: Django used `django.db.backends.postgresql`; the live non-secret probe recorded
  PostgreSQL 14.20. Credentials were not recorded.
- Checks: Django system check and migration sync passed. The orchestrator still owns the
  authoritative independent backend lane and full candidate validation.
- Dependencies, frontend, protected files: none changed by this repair.
- Residual risk: independent validation must reproduce both exact PostgreSQL runs and the selected
  backend lane before the candidate may be committed.
