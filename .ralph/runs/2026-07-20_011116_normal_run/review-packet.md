# Review Packet: 2026-07-20_011116_normal_run

## Result
Ready for independent validation

## Slice
010C2-manual-allocation-and-financial-reversal-controls

## Outcome

- Hardened the canonical 010C allocator with posted-SAP admission, allocation idempotency, exact
  schedule capacity, and immutable per-schedule application evidence.
- Added terminal exact approval plus public manual allocation for 010D manual-match exceptions.
- Added atomic append-only repayment reversal and reversal-ledger projection without rewriting the
  original receipt, allocation, schedule-application, or credit-ledger rows.
- Reconciled default Credit Manager/Accounts capture and allocation grants while leaving CFO,
  Auditor, manual-approval, and reversal authority default-denied.
- Added one additive migration and exact API contracts; no frontend or source-document changes.

## Traceability

- `functional-spec.md` M09-FR-009 says failed auto-matches require manual allocation with reason and
  approval; the code requires coherent 010D manual-match evidence and an immutable exact terminal
  approval, verified by
  `RepaymentAdjustmentApiTests.test_manual_exception_allocation_requires_exact_terminal_approval`.
- M09-FR-010–011 say balances update after posting and the repayment ledger is maintained; ordinary
  allocation now rejects pending/incoherent SAP truth and reconciles exact schedule/account/ledger
  amounts, verified by the admission and capacity tests.
- `screen-spec.md` S44/S46 says reversals require elevated permission/reason and immutable ledger
  history; the code appends compensating reversal/ledger rows and restores retained prior truth,
  verified by `test_reversal_appends_compensating_truth_and_preserves_original_rows`.
- `auth-permissions.md` §26.6 authorises Credit Manager and Accounts to capture/allocate while
  read-only roles only read; the seed matrix test proves exactly those defaults and no correction
  grant.

## Validation Evidence

- TDD RED/GREEN: `evidence/terminal-logs/*-red.log` and
  `evidence/terminal-logs/acceptance-matrix-green.log`.
- Focused reverse consumers: `reverse-consumers-green.log` — 62 tests, `OK`, four expected
  SQLite-skipped PostgreSQL-only tests, exit 0.
- PostgreSQL acceptance: `postgresql-adjustment-run-1.log` and run 2 — each found and passed exactly
  four tests, no skips, exit 0.
- Backend/migrations: `backend-check.log` and `migrations-check.log`, both exit 0.
- API/permission/ledger evidence: `evidence/financial-adjustment-contract.md`.
- Architecture finding closure: `review-closure-evidence.md` covers AR-010-ALLOCATION-001 and exactly
  AC-ALLOC-1 through AC-ALLOC-6.

## Review Notes

- High-risk source-silent role mappings are recorded as A-142 and A-143 and fail closed.
- `git diff --check` passed; protected-path scan returned no matches.
- Estimated product change is 1,991 lines, within the 2,000-line cap, with one migration.
- The orchestrator must run its authoritative complete backend coverage/full-suite and independent
  contract gates before commit/merge.

## Recommended Next Action

Run Ralph independent validation; commit, merge to `staging`, and push only if every gate passes.
