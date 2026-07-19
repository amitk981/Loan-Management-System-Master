# 010C Allocation Evidence Matrix

| Case | Receipt | Before P / I / C | Allocated P / I / C | Unallocated | After P / I / C | Outcome |
|---|---:|---:|---:|---:|---:|---|
| Below principal | 100,000.00 | 400,000.00 / 0.00 / 0.00 | 100,000.00 / 0.00 / 0.00 | 0.00 | 300,000.00 / 0.00 / 0.00 | allocated |
| Crosses principal | 60,000.00 | 40,000.00 / 10,000.00 / 5,000.00 | 40,000.00 / 10,000.00 / 0.00 | 10,000.00 | 0.00 / 0.00 / 5,000.00 | allocated_with_exception |
| Exact payoff | 400,000.00 | 400,000.00 / 0.00 / 0.00 | 400,000.00 / 0.00 / 0.00 | 0.00 | 0.00 / 0.00 / 0.00 | repaid |

The crossing case proves that configured outstanding charges are not silently consumed without an
approved waterfall. Its ledger credit is 50,000.00, not the 60,000.00 receipt; the remaining
10,000.00 stays explicit on the allocation. Exact replay retains one allocation, one audit, one
ledger entry, and one account transition.

Database evidence is in `terminal-logs/010C-red-database.log` and
`terminal-logs/010C-green-database.log`. PostgreSQL acceptance collects the single declared
five-request race test; the local SQLite run is intentionally skipped and the Ralph orchestrator
runs that contract twice on PostgreSQL.
