# Risk Assessment

Risk level: **Medium**, matching the selected slice.

- PostgreSQL locking: two queries that eagerly load nullable relations now use
  `select_for_update(of=("self",))`. This preserves serialization on the authoritative owning row
  while avoiding PostgreSQL's invalid attempt to lock the nullable side of an outer join.
- Approval action safety: the approval path already locks its application and appraisal separately;
  the corrected query continues to lock the case and reads general-meeting/exception relations as
  evidence. The historical five-race acceptance command passed twice on PostgreSQL.
- Template safety: successor creation continues to lock the immutable predecessor. Five concurrent
  identical requests produced one successor and one audit/version-history evidence set in each of
  two PostgreSQL runs.
- Contract impact: no schema, migration, endpoint, envelope, permission, state transition, audit
  payload, frontend, template lifecycle, or Annexure rule changed.
- External effects: no deployment, real communication, dependency installation, file download,
  commit, merge, push, or protected/source file modification was performed.

Residual risk: row-lock behavior is database-specific, so the orchestrator must still independently
repeat full PostgreSQL acceptance before committing. Local real-PostgreSQL runs are deterministic
and green; the ordinary 700-test SQLite suite remains green at 93% coverage.
