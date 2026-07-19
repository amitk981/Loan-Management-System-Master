# Review Packet: 2026-07-20_002403_repair

## Result
Ready for independent validation

## Slice
010D-bank-statement-matching-unmatched-receipts

## Failure and Root Cause

The independent 010D PostgreSQL acceptance test failed twice with
`FOR UPDATE cannot be applied to the nullable side of an outer join`. The manual-match service used
`select_for_update()` on a statement-line query that also `select_related()` the nullable matched
repayment. PostgreSQL attempted to lock both sides of the outer join and rejected the statement.

## Repair

Narrowed the statement-line lock to `select_for_update(of=("self",))`. This is the repository's
established PostgreSQL-safe query shape for eager-loading nullable relations while locking only the
owner row. The receipt remains separately locked immediately afterward, so concurrent matches still
serialize on the single receipt without weakening line ownership.

The `diagnosing-bugs` skill guided the repair through an exact red-capable PostgreSQL loop, ranked
hypotheses, a one-variable query correction, two green reruns, and cleanup verification.

## Source Traceability

- The slice and Epic 010 digest require one retained counterpart under real PostgreSQL contention.
  The code now locks the statement line and receipt as separate base rows; verified by
  `BankStatementMatchingPostgreSQLAcceptanceTests.test_concurrent_manual_matches_retain_one_statement_counterpart`.
- The 010D boundary says matching is evidence-only. The repair changes only SQL lock targeting and
  leaves allocation, SAP state, balances, schedules, and ledger paths untouched; verified by the
  direct-repayment/allocation focused regression set.

## Evidence

- RED: `evidence/terminal-logs/postgresql-lock-red.log` — exact declared test, PostgreSQL nullable
  outer-join lock error, explicit `EXIT_CODE=1`.
- GREEN 1: `evidence/terminal-logs/postgresql-lock-green.log` — exactly one test passed,
  `EXIT_CODE=0`.
- GREEN 2: `evidence/terminal-logs/postgresql-lock-green-2.log` — independent isolated database,
  exactly one test passed, `EXIT_CODE=0`.
- Focused gates: `evidence/terminal-logs/repair-focused-gates.log` — 19 impacted tests passed;
  Django check and migration sync passed; all explicit exit codes are zero.

## Review Focus

- Confirm the independent validator again observes exactly one PostgreSQL test and two successful
  executions.
- Confirm SQL generated for the line query locks only `bank_statement_lines`, while the following
  repayment query independently locks the selected repayment.
- Run the authoritative full backend coverage and migration/protected-path/diff gates before commit.

## Recommended Next Action
Run Ralph's full independent repair validation. Commit only if every declared gate passes.
