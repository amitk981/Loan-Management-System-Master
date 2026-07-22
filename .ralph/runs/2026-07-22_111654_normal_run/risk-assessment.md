# Risk Assessment

Risk level: Medium

- Selected slice: 011B-grace-period-tracking
- Mode: normal_run
- Change surface: one defaults migration, defaults workflow/model/API, the existing scheduler job
  vocabulary/task seam, canonical role catalogue, focused tests, and working API documentation.
- Financial/data-integrity risk: grace cure consumes the retained loan principal balance and never
  changes repayment/allocation facts. Expiry/task and assessment transitions are atomic and
  case-locked; database uniqueness prevents duplicate assessment type rows.
- Permission risk: assessment requires the exact permission, active Credit Assessment Team
  membership, case read authority, and persisted loan scope. Internal Auditor remains read-only.
- Privacy risk: scheduled outcomes contain counts only. Assessment evidence is validated through
  same-loan governed document ownership; audit evidence retains IDs and narrative but no new log
  output exposes borrower-sensitive content.
- Timing assumption: A-155 records the inclusive grace end date because the source does not state
  the exact on-date instant convention.
- Concurrency risk: the exact one-test PostgreSQL acceptance exercises five concurrent expiry runs
  and five concurrent assessment attempts. Local SQLite collection correctly skipped it; Ralph must
  execute the declared PostgreSQL acceptance twice during independent validation.
- Residual validation: the orchestrator owns the authoritative impacted/full backend lane,
  PostgreSQL execution, protected-path checks, and commit/merge decision. No frontend changed.
- Manual review required: independent Ralph validation only.
