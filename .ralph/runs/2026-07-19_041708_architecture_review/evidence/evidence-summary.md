# Architecture Review Evidence Summary

## Boundary

- Fixed point: `c90cb3263e3f5f34609baba3ba57ed67016b4768`.
- Reviewed commits: `bc476293` (009H9D), `7e88fe42` (009J), `eeb0ba7d` (009K).
- Product diff: 48 product/test files plus slice/API/digest evidence; production files were read-only.

## Independent review passes

- Standards pass found false/non-canonical workspace action authority, direct SAP-owner bypass,
  mixed real/mock Loan Account 360 truth, and unbounded full-portfolio composition.
- Spec pass found 009K's admitted S36 incompleteness, absent 009J/009K visual acceptance, Senior
  Finance's uncaught dependent permission, narrowed §30.2 filters, partial 009J negative matrices,
  and the still-missing MP14 opposite-order regression.
- Local reconciliation confirmed the nonexistent SAP permission, naive datetime transport,
  current-evidence bypass, and missing M07-FR-009 owner. These are grouped under corrective 009L.

## Executed evidence

| Evidence | Result |
| --- | --- |
| `green-009h9d-current-contract-tests.log` | 3 current copied 009H9D tests passed: incomplete provenance and both cross-kind authority cases. |
| `green-009j-009k-retained-tests.log` | 10 retained backend API tests passed. |
| `green-009j-009k-frontend-tests.log` | 14 focused frontend tests passed across four files. |
| `red-epic009-closure-probes.log` | 2 review-only probes failed on the intended assertions: 500 for admitted Senior Finance and projection of one incoherent approved row. |
| `datetime-contract-inspection.log` | Both real backend validators reject the raw naive timestamp used by the disbursement action forms. |

The old standalone `2026-07-19_014802` probe harness was also attempted and is retained as
`discarded-historical-probe-harness.log`. Its migration test deliberately rewinds the schema and its
teardown cannot traverse the later 0013 migration, so it is not used as current closure evidence.
The same three assertions were copied into current product tests by 009H9D; those current tests are
the green evidence above.

## Contract and epic audit

- 009K's own committed review packet says S36 and screenshots remain open despite its Complete
  status. 009J's evidence likewise records zero of four required screenshots.
- S37 advertises `finance.sap_customer_code.complete`; the catalogue, auth source, real endpoint,
  and working contract all require `finance.sap_request.complete`.
- The browser forwards `datetime-local` form strings unchanged. SAP completion and transfer success
  require timezone-aware ISO-8601 values and reject the submitted shape.
- M07-FR-009 appears in source but has no implementation, queued owner, or explicit assumption.
  M07-FR-001-008/010 and M08-FR-001-011 have retained backend owners, subject to the staff
  reachability/evidence defects recorded in 009L.
- No slice is Blocked. `docs/working/CONTEXT.md` still accurately describes the repository boundary.

## Scope

No production code, protected file, source document, orchestrator state/progress, mechanical
handoff, or historical run evidence was edited. The candidate contains review docs, one corrective
slice/dependency, and this run's evidence only.
