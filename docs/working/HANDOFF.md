# Ralph Handoff

## Last Run
2026-07-13_160532_normal_run

## Current Status

007E is complete. The approval-owned conflict module evaluates typed persisted borrower,
Director-relative, and material-interest declarations plus immutable application/appraisal maker
facts for each case cycle. Enrichment preserves ordered required-authority history, freezes unique
exclusions/reasons, and sets the general-meeting-evidence flag.

Excluded actors retain limited history/detail read but never queue or action authority. Frozen
same-role committee alternates preserve the matrix role/count; missing CFO/Director authority
closes the case as `blocked_by_conflict` without a sanction. Approve/reject/return use exact
`CONFLICTED_APPROVER_NOT_ALLOWED` details and add only the cycle-attributed COI-006 denial audit.
Reasoned abstention uses the immutable action ledger and either assigns a frozen alternate or
creates a communication-backed conflict-blocked outcome. Prior-cycle exclusions/actions never
populate a later cycle.

## Validation

TDD red/green evidence covers frozen maker facts, declarations, enrichment, exact denial/audit,
alternate authority, satisfiable and blocked abstention, and malformed snapshot rejection. The
focused approval suite passes 70 tests with two expected PostgreSQL-only skips. Backend check and
migration sync pass; the full 637-test suite passes with 19 expected PostgreSQL-only SQLite skips
and 93% coverage. Frontend build/typecheck/lint and all 208 tests pass.

The first full backend attempt exposed a migration-graph interaction with the legacy witness
migration test. The approvals migration dependency was narrowed from applications 0014 to the
earliest schema it consumes (0011); the three migration tests plus approval regressions then passed,
followed by the full green suite. No protected files or source documents changed.

## Next Run

Architecture review is now due after four completed slices. After that review, run
`007F-exception-approval-workflow`; it is sharpened for conflict-blocked outcomes and COI-006
zero-mutation register behavior. `007G` is also sharpened to consume the immutable per-cycle
general-meeting flag without re-evaluating live conflict facts.
