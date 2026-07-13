# Review Packet: 2026-07-10_230547_repair

## Result
Success

## Slice
006F4-postgresql-credit-concurrency-acceptance

## Outcome

- PostgreSQL 14.20 executed all five authoritative races twice with zero skips.
- Fixed PostgreSQL-only fixture binding and retired workflow-event assertions without weakening
  concurrency outcomes.
- Restricted eligibility's application lock to the base table row, eliminating PostgreSQL's
  nullable-outer-join `FOR UPDATE` failure while retaining application-first serialization.
- Added and exercised a fail-closed run-packet verifier.

## Source Traceability

- `docs/source/codebase-design.md` §26.3 says financial modules require concurrency tests. The code
  exercises `LoanLimitCalculator` and `AppraisalWorkflow` public interfaces with five independent-
  connection transaction races, verified by both final PostgreSQL logs.
- `docs/source/data-model.md` §34 says loan-limit assessment, audit, and workflow evidence update
  atomically. The two loan-limit tests assert one stable assessment, complete projections, matching
  audit/workflow facts, and no invalid loser evidence.
- `docs/source/codebase-design.md` §37.3 requires row locks in financial workflows. The production
  module now locks `LoanApplication` with `select_for_update(of=("self",))`; the two loan-limit races
  verify the lock serializes before payload/state mutation.
- 006F3/006G contracts require one terminal appraisal/rejection/sanction winner and no loser success
  writes. `AppraisalConcurrencyTests` and `SanctionSubmissionConcurrencyTests` verify those exact
  outcomes on PostgreSQL.

## Changed Behavior and Files

- `sfpcl_credit/credit/modules/eligibility_assessment.py`: base-row-only application lock.
- Three PostgreSQL concurrency test classes: preserve inherited static fixtures and assert canonical
  workflow-event fields/decision identity.
- Ralph slice/digest/state/progress/handoff and two next-slice requirement sharpenings.
- No frontend, API, schema, migration, dependency, formula, permission, or state-machine change.

## Evidence

- `evidence/failure-diagnosis.md`
- `evidence/postgresql-acceptance.md`
- `evidence/terminal-logs/postgresql-concurrency-initial-red.log`
- `evidence/terminal-logs/postgresql-concurrency-green-1.log`
- `evidence/terminal-logs/postgresql-concurrency-green-2.log`
- `evidence/terminal-logs/run-packet-verifier-red.log`
- `evidence/terminal-logs/run-packet-verifier-green.log`
- `evidence/terminal-logs/backend-coverage-tests.log`
- `evidence/terminal-logs/backend-coverage-report.log`
- Frontend/check/migration logs in `evidence/terminal-logs/`

## Recommended Next Action
Run 006G2, retaining this exact five-race PostgreSQL acceptance after moving approval-case ownership
behind its module interface. Then complete 006H2 and 006H3 before the Epic 006 tracer.
