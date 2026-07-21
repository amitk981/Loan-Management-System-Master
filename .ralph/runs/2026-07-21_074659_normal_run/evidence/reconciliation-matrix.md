# Statement Reconciliation Matrix

| Case | Canonical source | Export proof | Result |
|---|---|---|---|
| Full funded history | `GET .../ledger/` disbursement row | Parsed CSV debit/credit/running total equal selector; opening 0.00 and closing 400000.00 | Pass |
| Exact replay | Same account/range/key twice | One `ScheduledJob`, one added `DocumentFile`, identical response/checksum | Pass |
| Borrower own loan | Active portal member/account relation | Same canonical projection, masked bank reference | Pass |

Focused evidence: `terminal-logs/final-focused-tests.log` and `terminal-logs/statement-portal-green.log`.
