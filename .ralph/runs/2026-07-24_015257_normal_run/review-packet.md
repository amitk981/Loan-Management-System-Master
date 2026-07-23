# Review Packet: 2026-07-24_015257_normal_run

## Result
Ready for independent validation

## Slice
012A2-finance-and-servicing-report-catalogue

## Delivered

- Registered all nine required stable report codes.
- Added scoped owner-backed selectors for Credit Sanction, Exception, Security Custody, SAP
  Pending, full Disbursement, Repayment, Interest Invoice, Interest Accrual, and CFO Quarterly MIS.
- Added filtered source totals for Credit Sanction, Disbursement, Repayment, and Interest Accrual
  without changing existing owner endpoint contracts.
- Documented codes, filters, fields, totals, permissions, scope, masking, and reconciliation in
  `docs/working/API_CONTRACTS.md`.
- Recorded the bounded source-silent route/filter/timestamp decision as A-169.

## Source-to-code traceability

- The source says the critical catalogue includes these finance/servicing reports and must be
  correctly permissioned (`implementation-roadmap.md` §17.3/R8-AC-001). The registry contains all
  nine codes, verified by
  `ReportCatalogueApiTests.test_all_required_catalogue_codes_are_registered_and_default_deny`.
- The source says S69 reports drill into sanction, security, SAP/disbursement, repayment, interest,
  and monitoring truth (`screen-spec.md` S69). Each selector delegates to the owning register,
  owner projection, evidence coordinator, or canonical scoped-account selector, verified by the
  nine seeded reconciliation tests in `test_report_catalogue_api.py`.
- The source says reports are paginated, role/object scoped, minimised, and masked
  (`api-contracts.md` §40; `auth-permissions.md` report/export rules;
  `security-privacy.md` §32). Every seeded report asserts standard pagination and a 40-query
  ceiling; invalid filters return 400; no-access returns 403 without data/totals; custody and SAP
  tests assert restricted values are absent.

## Evidence

- RED/GREEN: `evidence/terminal-logs/*-red.log` and matching `*-green.log`.
- Final focused catalogue and foundation reports: `evidence/terminal-logs/final-focused-tests.log`
  — 23 tests passed.
- Focused plus reverse consumers: `evidence/terminal-logs/focused-and-reverse-consumer-green.log`
  — 28 tests passed.
- Filter matrix/query bounds: `evidence/terminal-logs/catalogue-filter-matrix.log` and
  `evidence/terminal-logs/report-catalogue-query-bounds.log` — nine catalogue tests passed.
- Django/migrations: `evidence/terminal-logs/final-django-check.log` and
  `evidence/terminal-logs/final-migrations-check.log`.
- Code/source/permission/reconciliation matrix: `evidence/report-catalogue-matrix.md`.

## Review notes

- No frontend, export generation, model, migration, dependency, routing, or permission-seed change.
- The failed intermediate reverse-consumer log records the detected owner pagination regression;
  the later green pack proves the compatibility repair.
- A local Black check was unavailable because Black is not installed in the pinned backend
  environment; it is not a configured Ralph gate. Compile, Django, migration, focused, and
  reverse-consumer checks passed.

## Recommended Next Action
Run Ralph's independent selective backend validation and commit only if it passes.
