# Review Packet: 2026-07-20_204224_normal_run

## Result
Ready for independent validation

## Slice
CR-014-rate-current-date-terminal-finalizer

## Outcome

The caller-controlled future-date mutation seam was removed. One server-date owner now publishes a
Loan Account's current rate through immutable idempotency/audit evidence, a bounded Celery callable,
and bounded list/detail selection. Stale-but-valid rate projections remain in collection identity
and are converged before serialization. Automated runs use truthful system attribution, while
manual publication requires both management authority and the loan-owned account scope.

## Traceability

- The source says floating rate changes are versioned/effective-dated and communicated
  (`functional-spec.md` M10-FR-001–002, BR-064–065). The code continues to resolve the approved
  version by explicit calculation date while current publication uses only `timezone.localdate()`;
  verified by `RateCurrentDateFinalizerTests.test_before_date_after_matrix_aligns_reads_and_interest_consumers`.
- The data model says `loan_accounts.current_interest_rate` and append-only
  `interest_rate_histories` retain current/history truth (§§18.1, 18.5), and transactional changes
  are atomic (§34). The code locks one account and atomically writes its scalar, audit, and immutable
  projection decision; verified by the replay test and declared PostgreSQL race class.
- The API/design sources require idempotency and tests through module interfaces (`api-contracts.md`
  §45.2; `codebase-design.md` §§26, 38). Exact replay returns the retained decision; changed and
  cross-account keys conflict with zero duplicate effects, tested only through public owner/read
  interfaces.
- Invoice, accrual, and capitalisation arithmetic were not changed. Focused reverse-consumer tests
  prove invoice/accrual rate versions still follow approved effective periods and capitalisation
  retains its source-invoice rate version.
- Independent standards/spec review findings were addressed before handoff: the scalar mutation
  now sits behind a loan-owned facade, decision writes reject direct/bulk mutation, automated work
  no longer impersonates a historical approver, distinct-account bounded processing is exercised,
  and retained evidence repairs a stale scalar deterministically.

## Verification

- RED: the permanent future-publication test failed because the safe public owner did not exist.
- GREEN: the focused owner/runtime set passed locally; nine PostgreSQL-only tests (five current
  finalizer plus four predecessor tests) were collected and skipped on SQLite.
- Reverse consumers and query ceiling: four focused tests passed.
- Loan Account read module: 17 tests passed.
- Django system check and migration sync: passed.
- Full suite/coverage and twice-run PostgreSQL acceptance: delegated to Ralph as required.

## Review Notes

- No frontend, API response-shape, formula, notice, retained-consumption, or scheduler-cadence change.
- No protected file or `docs/source/` edit.
- The PostgreSQL race assertions need independent execution; local skip is not claimed as race proof.
- The Celery task returns a JSON-serializable processed-count/account-ID summary rather than model
  or dataclass values.

## Recommended Next Action
Run independent validation, including the exact five-test PostgreSQL class twice, full coverage, and
the migration graph. Commit only if all gates pass.
