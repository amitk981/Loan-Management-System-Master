# Report Reconciliation and Role-Denial Evidence

## System-of-record reconciliation

- The S69 table renders only the `data` rows returned by the selected 012A endpoint.
- The record count and page labels render the response `pagination.total_count`, `page`, and
  `total_pages`; no client-side total is inferred from the visible page.
- The portfolio behavior fixture reconciles `LN-REPORT-001`, `Seeded Report Member`, and
  `₹1,30,000.00` to the returned loan-account projection and reconciles the displayed `1 record`
  to `pagination.total_count = 1`.
- Evidence: `evidence/terminal-logs/report-screen-green.log` and
  `evidence/terminal-logs/report-focused-tests.log`.
- Backend 012A reconciliation and role/object-scope regressions remain green across all six report
  endpoints. Evidence: `evidence/terminal-logs/report-api-regressions.log`.

## Filters, sorting, and pagination

- The active `as_of_date=2026-06-30` and `status=active` filters remain in the public service
  request after ordering changes to `total_outstanding` and after moving from page 1 to page 2.
- Backend ordering uses explicit per-report public-field allowlists and stable identity/date
  tie-breakers. `ordering=pan_encrypted` is rejected with a 400 field error.
- Evidence: `evidence/terminal-logs/report-filter-sort-pagination-green.log`,
  `evidence/terminal-logs/report-ordering-red.log`, and
  `evidence/terminal-logs/report-ordering-green.log`.

## Nondisclosure and role denial

- A backend 403 is propagated by the service and the screen clears previously visible rows and
  totals before rendering `Report access denied`.
- Loss of all eligible report permissions replaces the report surface with `Access Restricted`;
  the prior borrower and account facts are absent.
- Evidence: `evidence/terminal-logs/report-status-permission-green.log`.

## Trusted browser acceptance

- The exact declared spec exists at `e2e/reports-exports-audit-explorer.e2e.spec.ts` and asserts
  the S69 filter/order/page request sequence, backend record count, read-only network behavior, and
  required `report-results.png` output.
- Two local attempts reached healthy localhost backend/frontend servers, but Chrome aborted before
  page creation. The independent re-probe reproduced the same launch-only failure. No screenshot
  was fabricated.
- Evidence: `evidence/terminal-logs/report-browser-run-1.log`,
  `evidence/terminal-logs/report-browser-run-1-retry.log`, and
  `evidence/terminal-logs/browser-infrastructure-reprobe.log`.
- Per the slice runtime rule, trusted independent validation must execute the exact spec twice and
  own the final browser-acceptance decision when Chromium is available.
