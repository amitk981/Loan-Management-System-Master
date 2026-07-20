# Final Summary

Implemented slice `010H2-interest-calculation-payment-and-replay-owner-closure`.

## Delivered

- One shared as-of `simple_daily` decision segments annual invoices and monthly accruals at retained
  principal and effective-rate boundaries, including leap-day behavior.
- Invoice payments are derived from exact schedule-application evidence. Capitalisation includes
  eligible applications through 30 April, excludes later/unrelated payments, subtracts interest once,
  and excludes tax, fees, and charges from principal.
- Capitalisation atomically reconciles principal, interest, total outstanding, schedule status,
  immutable invoice/payment/schedule/ledger evidence, audit, queued email, letter document, and a
  durable hard-copy task.
- Generation, issuance, accrual posting, and capitalisation now replay stored original responses;
  later provider/SAP state cannot rewrite financial replay truth.
- Consumed calculation configuration and terminal invoice/accrual/capitalisation evidence reject
  instance/queryset/bulk mutation. Invoice issue authority and communication template are frozen at
  generation.
- Added the exact five-test `InterestAccountingOwnerPostgreSQLAcceptanceTests` class.

## Evidence

- Red/green logs: `evidence/terminal-logs/ac-int-*.log`.
- PostgreSQL: both `postgresql-owner-pass-1.log` and `postgresql-owner-pass-2.log` ran five tests,
  passed, and recorded `EXIT_STATUS=0`.
- Reverse consumers: 44 tests passed with exit 0.
- Django check and migration drift check passed.
- Architecture closure mapping: `review-closure-evidence.md`.

No dependency was added, no frontend was changed, and no source/protected file was modified. The
orchestrator owns complete-suite coverage, state/status bookkeeping, commit, merge, and push.
