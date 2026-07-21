# Risk Assessment

Risk level: Medium (matches the selected slice)

## Financial and data-integrity risks

- Quarter-end numbers are material management information. Generation reads only owner records at
  or before the cutoff, freezes their IDs/calculation versions, and retains typed totals plus rows.
- Missing default, recovery, closure, grievance, compliance, and related later-epic facts remain
  explicitly `unavailable`; nullable typed counts must not be interpreted as zero.
- Reports are revisioned rather than overwritten. Model/queryset guards protect snapshots and
  reviewed evidence through ORM paths, while PostgreSQL uniqueness, row/advisory locks, and exact
  idempotency bindings protect concurrent generation and review.
- Account-scope changes can intentionally make an old report nondisclosing to a reader whose current
  canonical scope no longer contains the complete frozen portfolio.

## Operational risks and mitigations

- PDF/XLSX artifacts are stored through the existing local document-storage seam with checksums;
  production durability remains the responsibility of that configured storage adapter.
- Generation has a measured ceiling of 40 queries for the seeded report test. Prefetches keep the
  query count bounded with portfolio size, but large-volume memory and document-size profiling is
  outside this slice.
- A PostgreSQL run passed the exact two-test contention class locally. Ralph's independent validator
  remains authoritative and will repeat the declared contract twice in isolated databases.

No protected files, source documents, frontend assets, dependencies, or external systems changed.
