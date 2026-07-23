# Report API Validation Evidence

## Captured responses

`terminal-logs/report-api-response-examples.log` contains response bodies captured while seven
passing Django tests executed against isolated test databases. It includes:

1. Application pipeline: one Loan Request Register row; `total_count=1`.
2. Documentation readiness with `status=pending`: one in-progress checklist, two required items,
   one complete item, one pending item, and blocker `loan_agreement`; `total_count=1`.
3. Disbursement pending: one initiated disbursement with pending authorisation and transfer;
   `total_count=1`.
4. Loan portfolio at the inclusive cutoff: one canonical loan account; `total_count=1`.
5. DPD at the inclusive cutoff and `one_to_two_years` bucket: the latest qualifying persisted
   snapshot; `total_count=1`.
6. Compliance dashboard for `FY2026-27`: one Section 186 row and one NBFC principal-business row;
   `total_count=2`.

The same captured log contains an authorised application-pipeline empty page
(`data=[]`, `total_count=0`) and a forbidden response containing only the standard error/meta
envelope. The forbidden body has neither `data` nor `pagination`, so it discloses no totals. A 401
example is retained beside them.

## Reconciliation

The 14-test focused suite in `terminal-logs/report-api-focused-suite.log` compares response
identifiers, totals, canonical statuses, amounts, cutoff behavior, latest DPD selection, checklist
counts/blockers, and compliance flags directly with persisted owner rows. All 14 tests passed.

The six representative fixture counts were application `1`, documentation `1`, disbursement `1`,
portfolio `1`, DPD `1`, and compliance `2`. Boundary/filter tests also cover inclusive application
dates, the loan-account creation cutoff, the DPD snapshot cutoff, financial year, controlled
statuses/buckets, combined filters, malformed dates, reversed ranges, and unknown parameters.

## Bounded and read-only behavior

`terminal-logs/report-api-query-count-green.log` records `MEASURED_QUERY_COUNT=6` for a paginated
application-pipeline request and proves stable page ordering. The behavior test caps it at 10 and
also proves report reads do not add audit rows or alter Loan Request Register rows.

`terminal-logs/report-api-reverse-consumers.log` records 37 passing existing dashboard, DPD,
disbursement-workspace, and statutory-tracker tests. This pack exercises the owning selectors after
the report reads and found no owner-state regression.

## Focused gates

- Report API suite: 14 passed.
- Reverse-consumer pack: 37 passed.
- Django system check: no issues.
- Migration synchronization: no changes detected.
- Targeted changed-file AST and diff whitespace checks: passed.

The implementation agent intentionally did not run the complete backend suite or coverage. Ralph's
independent validator owns the authoritative risk-selected backend lane.
