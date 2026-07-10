# Slice 006F4: PostgreSQL Credit Concurrency Acceptance

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Close the repeated no-merge acceptance failure by executing every Epic 006 row-lock race on real
PostgreSQL and correcting any outcome that does not serialize exactly as the public contracts say.

## Depends On
- 006E4

## Source / Review References
- `docs/source/codebase-design.md` §22.3, §26.3, and §37.3
- `docs/source/data-model.md` §34
- `docs/slices/006D2C-loan-limit-concurrency-and-boundary-regression.md`
- `docs/slices/006F3-appraisal-lock-order-and-postgresql-concurrency-closure.md`
- `docs/slices/006G-submit-to-sanction.md`
- `docs/working/ASSUMPTIONS.md` A-055
- `docs/working/REVIEW_FINDINGS.md` entry for this review

## Scope

- Run, without changing or weakening their assertions, all tests in
  `LoanLimitConcurrencyTests`, `AppraisalConcurrencyTests`, and
  `SanctionSubmissionConcurrencyTests` using
  `sfpcl_credit.config.postgres_test_settings` and the mandated Ralph interpreter.
- Five tests must execute with zero skips: two loan-limit races, two appraisal/rejection races, and
  one duplicate sanction-submission race. Test collection, SQLite skips, missing driver/server,
  connection failure, mocked row-lock assertions, or sandbox denial is failure evidence.
- Diagnose any PostgreSQL failure and make the smallest public-module correction that preserves the
  single application -> appraisal -> history/rejection -> approval-case order, one winning terminal
  outcome, one complete evidence set, and no loser success writes.
- Add a static/run-artifact regression that prevents a run packet from claiming success when the
  required PostgreSQL command did not execute all five tests.

## Test Cases

- Existing five PostgreSQL tests execute unchanged first; save their initial output.
- If a real race fails, save red evidence before the correction and green output after it.
- Repeat the combined acceptance command at least once to expose timing-dependent flakiness.
- Full SQLite/default regression may retain explicit PostgreSQL skips, but those skips never count
  as this slice's acceptance.

## Evidence Required

PostgreSQL version/non-secret settings, both complete combined command outputs with five executed
tests and zero skips, any red/green repair output, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- The five authoritative races pass twice on real PostgreSQL with zero skips.
- The slice is not marked Complete and must not merge if PostgreSQL execution is unavailable.
