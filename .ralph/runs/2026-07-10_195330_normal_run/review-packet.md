# Review Packet: 2026-07-10_195330_normal_run

## Result
Failed acceptance; do not commit or merge.

## Slice
`006F3-appraisal-lock-order-and-postgresql-concurrency-closure`

## Candidate change

- `AppraisalWorkflow` uses one private application-first locking implementation for submit,
  prerequisite revalidation, and review; create/update already use application first.
- Existing review-history rows are locked only after application and appraisal. Rejection-note work
  remains behind its public module seam and occurs after those locks.
- PostgreSQL `FOR UPDATE OF self` avoids accidentally locking nullable joined user rows. The same
  correction was necessary on the unchanged loan-limit concurrency path's application lock.
- New PostgreSQL transaction tests cover rejected review versus stale PATCH and competing terminal
  decisions, including exact history/audit/workflow/rejection-note cardinality and loser no-write
  assertions.

## Traceability

- Source `codebase-design.md` §12.3 and §26.1-§26.3 says appraisal behavior stays behind
  `AppraisalWorkflow` and workflow/financial behavior is tested transactionally through the module
  interface. The candidate keeps the public interface unchanged and tests only that interface.
- Source `data-model.md` §14.4 and §34 requires appraisal decision facts and related workflow writes
  to be transactionally coherent. Tests require one terminal projection, one native immutable
  decision, and matching audit/workflow decision UUIDs.
- Source `api-contracts.md` §3 and §24.4 requires backend-enforced transitions, immutable approval
  evidence, snapshots, actor/time/reason/audit, and the dedicated review action. No payload or API
  response contract changed.
- Architecture review `2026-07-10_190455_architecture_review` requires application -> appraisal ->
  rejection/history order and real PostgreSQL outcome proof. The implementation candidate addresses
  the order; the proof remains unmet because zero PostgreSQL tests executed.

## Validation

- Focused credit/appraisal: 52 passed, 2 PostgreSQL-only skipped under SQLite.
- Full backend: 365 passed, 4 PostgreSQL-only skipped; coverage 94% (floor 85%).
- Django check and migration sync: passed.
- Frontend lint, typecheck, 107 tests, and build: passed.
- Combined PostgreSQL acceptance: failed before execution with sandbox socket `Operation not
  permitted`; four tests found, zero executed.

## Recommended next action

Run Ralph repair in an environment allowed to connect to PostgreSQL. Re-run the exact combined
four-test command with zero skips, diagnose any actual database/test failure, then repeat all gates.
Do not promote 006G until 006F3 is green and Complete.
