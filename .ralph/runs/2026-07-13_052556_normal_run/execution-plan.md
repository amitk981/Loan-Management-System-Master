# Execution Plan

Selected slice: `007A2-approval-configuration-history-and-committee-authority-closure`

## Scope and approach

1. Add focused public-interface tests, one red/green tracer at a time, for full-history rule
   overlap, lifecycle resolution, committee authority and dated resolution, bounded pagination,
   malformed/forbidden zero-write behavior, retained projection history, and PostgreSQL races.
2. Deepen the approvals module behind two approval-owned resolver/configuration interfaces. Enforce
   lifecycle and authority invariants transactionally, preserving zero-write losers and immutable
   retained rows.
3. Add non-destructive database constraints/indexes and update the documented API contract for the
   paginated collections and committee resolver behavior.
4. Run focused SQLite tests throughout, migration/check gates, the direct PostgreSQL concurrency
   class twice, then all backend and frontend quality gates required by Ralph.
5. Save red/green, migration, race, and gate evidence; update slice/state/progress/handoff and the
   run review artifacts. Sharpen only the next one or two Not Started slices using already-opened
   Epic 007 material.

## Permissions and risk

- Planned edits are limited to `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`,
  `.ralph/state.json`, `.ralph/progress.md`, and this run folder, all writable by the active policy.
- No protected or source file will be modified.
- Risk is High because approval authority, historical routing, and concurrent configuration writes
  are security/business-critical. The standing approval entry is present and not revoked.

## Verification

- Focused red and green commands use `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- `manage.py check`, `makemigrations --check`, focused/full tests with coverage, and configured
  frontend build/typecheck/lint/tests.
- `ApprovalMatrixConcurrencyTests` under PostgreSQL settings twice, with exact test names retained.
