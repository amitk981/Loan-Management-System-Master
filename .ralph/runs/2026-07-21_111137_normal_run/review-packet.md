# Review Packet: 2026-07-21_111137_normal_run

## Result
Ready for independent validation

## Slice
010MA-servicing-account-and-repayment-frontend-wiring

## Implementation Summary

- Added one authenticated servicing transport seam for canonical schedule, ledger, repayment,
  statement-exception, direct capture/SAP/allocation, standard pagination, and backend error flows.
- Wired Loan Account 360 and Repayments Hub to backend projections with truthful pagination,
  loading/empty/error/unauthorised states, canonical refresh, stale-response suppression, and no
  client-owned financial/matching policy.
- Added the narrow scoped `GET /api/v1/loan-accounts/{id}/repayments/` projection required for S45,
  including retained allocation, SAP, statement, and subsidiary reconciliation evidence.
- Added deterministic real-auth seed permissions and the exact two-scenario trusted-browser spec
  with declared screenshot names.

## Traceability

- Requirements 1-2: `servicingApi.ts`, `LoanAccount360.tsx`, and `RepaymentLedger.tsx` implement
  authenticated envelopes, backend Money values, schedule/ledger pagination, account-reset behavior,
  and error states. Covered by servicing API, Loan Account 360, precision, and full frontend tests.
- Requirement 3: the combined direct action requires source role plus three permissions, uses stable
  capture/allocation idempotency keys, stops exact capture replay, renders backend allocation, and
  exposes duplicate/validation denial without retry. Covered by service and hub tests plus browser
  action assertions.
- Requirement 4: the backend repayment read projection and independent statement queues expose only
  retained canonical matching/allocation/reconciliation facts. Covered by three backend projection
  tests and hub queue/pagination/race tests.
- Requirement 5 and mock removals: owned surfaces reuse existing UI classes/components and contain no
  mock import, inline business fixture, `.reduce` financial calculation, or allocation preview.
  Static audits and A-152 record the local composition boundary.

## Independent Two-Axis Review

- Standards findings closed: source-role gating, independent statement pagination, A-152 component
  justification, and endpoint authority/scope/strict-pagination proof.
- Spec findings closed: statement states/pages, stale cross-loan responses, account page reset,
  precision-safe Money rendering, subsidiary loading/error/unauthorised behavior, and duplicate /
  validation no-retry proof.
- Final parallel re-review found no regression and no remaining standards or spec finding.

## Evidence

- Backend RED/GREEN: `backend-read-projection-red.log`, `backend-read-projection-green.log` (3 tests),
  `servicing-real-auth-seed-red.log`, `servicing-real-auth-seed-green.log`, and
  `direct-repayment-impacted-green.log` (28 tests).
- Frontend RED/GREEN: `servicing-api-red.log`, `servicing-api-green.log`,
  `servicing-workspaces-red.log`, `servicing-workspaces-green.log`,
  `independent-review-red.log`, and `independent-review-green.log` (20 tests).
- Configured frontend gates: `frontend-full-tests.log` (47 files / 378 tests),
  `frontend-typecheck.log`, `frontend-lint.log`, and `frontend-build.log`, all exit 0.
- Backend consistency: `backend-check.log` and `backend-migrations-check.log`, both exit 0.
- Browser/static: `servicing-browser-collection.log` lists 2 declared Chromium tests;
  `servicing-static-audits.log` exits 0. `servicing-browser-local.log` records only sandbox Chromium
  launch `SIGABRT`, before test execution.

## Independent Validation Notes

- Run the declared trusted-browser contract twice outside the coding sandbox and retain
  `servicing-ledger.png` and `direct-repayment-posting.png`; local screenshot evidence is intentionally
  absent because Chromium could not launch.
- Run the orchestrator-owned complete backend suite under coverage and all configured risk gates.

## Recommended Next Action
Proceed with independent Ralph validation; on success, let the orchestrator commit and merge the slice.
