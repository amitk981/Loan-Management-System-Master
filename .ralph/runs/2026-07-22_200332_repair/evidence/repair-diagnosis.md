# Repair Diagnosis Evidence

## Failure

The authoritative complete backend lane failed only at
`DefaultGraceAssessmentApiTests.test_early_paid_closed_foreign_and_unauthorised_assessments_are_rejected`.
After asserting that assessment of a closed account is rejected, the legacy test attempted to clear
`closed_at` through `LoanAccountQuerySet.update()`. Slice 011G intentionally makes that public mutation
path reject every closed account.

## Root cause

The test combined five denial scenarios on one account and placed the closed scenario before two
later scenarios, requiring an invalid setup-only reopening. The production guard matches
`product-requirements.md` §11.28 and `MOD-CLOSURE-010`; it was not weakened.

## Minimal repair

The same test now executes foreign-scope and unauthorised requests while the account is still open,
then marks the account closed and asserts the closed rejection last. All response, zero-write, and
retained case-state assertions remain in the same test.

## Feedback loop

| Phase | Command/label | Result | Log |
| --- | --- | --- | --- |
| RED | Exact failing Django test label | Reproduced `ValidationError: Closed loan accounts are read-only` | `terminal-logs/01-default-grace-closed-fixture-red.log` |
| GREEN | Exact failing Django test label | 1 test passed | `terminal-logs/02-default-grace-closed-fixture-green.log` |
| Regression | Default-grace module + closure API + direct repayment API | 25 tests passed | `terminal-logs/03-focused-regression-green.log` |
| Static | Django check + migration consistency + diff whitespace | Passed; no migration changes | `terminal-logs/04-static-checks-green.log` |

The complete backend coverage command is deliberately left to Ralph's independent validator, as the
repair prompt forbids the agent from running the complete suite or full coverage itself.
