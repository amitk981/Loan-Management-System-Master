# Review Packet: 2026-07-19_215119_normal_run

## Result
Ready for independent validation

## Slice
010A-loan-account-schedule-and-ledger

## Delivered

- Added constrained `repayment_schedules` persistence from source data-model §18.3.
- Added permission/object-scoped, strictly paginated schedule and ledger GET interfaces.
- Added a process coordinator over loan, SAP, and disbursement owner interfaces.
- Added a historical disbursement evidence interface that preserves the opening row after later
  servicing balances/status advance while rejecting immutable funded-amount/activation-date drift.
- Extended the API contract, response examples, and assumptions A-136/A-137.

## Traceability

- The source doc says repayment schedules retain the §18.3 fields and unique
  `(loan_account, installment_number)` (`docs/source/data-model.md` §18.3); the code adds
  `RepaymentSchedule` plus migration constraints; verified by
  `test_authorised_reader_gets_ordered_decimal_schedule_truth` and
  `test_database_rejects_duplicate_installments_and_negative_financial_truth`.
- The source doc says S46 ledger rows expose date/type/reference/debit/credit/running balances/
  actor/SAP status/remarks and remain immutable (`docs/source/screen-spec.md` S46); the coordinator
  projects the canonical successful disbursement without copying it; verified by
  `test_ledger_projects_one_canonical_disbursement_without_copying_it`.
- The slice says later repayment/interest movements must append without losing the opening row;
  historical evidence relaxes later-owned balances/status only; verified by
  `test_later_servicing_balances_preserve_schedule_and_opening_disbursement` and
  `test_historical_ledger_rejects_drifted_immutable_activation_amount`.
- Auth §19.3 requires loan-object scope plus `finance.loan_account.read`; both endpoints use the
  canonical account scope and nondisclosing 404; verified by
  `test_schedule_and_ledger_enforce_auth_role_permission_and_object_scope`.

## Independent Review

- Standards axis: initial hard findings for `loans -> disbursements` dependency direction and an
  unsupported persisted status were fixed; the follow-up immutable-fact finding was fixed. Final
  result: no hard documented-standard violations.
- Spec axis: initial High servicing-balance and Low incomplete no-write findings were fixed; the
  future SAP-lifecycle Medium and final documentation inconsistency were fixed. Final result: no
  implementation-level spec issue.
- Judgement call retained: the coordinator uses a local decimal-string formatter, consistent with
  existing loan projections; introducing a repository-wide Money utility is outside this slice.

## Evidence

- RED/GREEN tracer and corrective logs: `evidence/terminal-logs/*-red.log` and `*-green.log`.
- Focused 10-test contract: `evidence/terminal-logs/schedule-ledger-focused-green.log`.
- Six Epic 009 reverse consumers: `evidence/terminal-logs/epic009-reverse-consumers.log`.
- Django check/migration sync: `evidence/terminal-logs/backend-check-and-migrations.log`.
- Constraint SQL: `evidence/terminal-logs/repayment-schedule-migration-sql.log`.
- Exact response shapes: `evidence/api-response-examples.md`.

## Substantive Decisions and Residual Risks

- A-136 records the conventional subresource paths and owner-backed ledger projection.
- A-137 keeps persisted statuses to `pending`/`paid`/`overdue`; partial display semantics remain
  owned by the future allocation slice.
- Schedule ingestion/generation and every servicing mutation remain out of scope.
- The authoritative complete backend suite/coverage, protected-path, migration, and diff gates are
  intentionally left to the Ralph orchestrator.

## Recommended Next Action

Run Ralph independent validation; commit/merge only if every orchestrator gate passes.
