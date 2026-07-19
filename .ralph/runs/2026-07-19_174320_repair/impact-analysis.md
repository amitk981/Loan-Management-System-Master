# Impact Analysis

## Demonstrated Failure

The retained trusted browser run completed real staff login, Loan Account reads, payment initiation,
and CFC authorisation against Django. Its real transfer-success request then returned HTTP 400 with
`disbursed_at: Must not be before CFC authorisation.` Six of nine screenshots were captured before
that failure. The repair is therefore bounded to the browser contract's transfer timestamp/evidence;
it does not require changing screenshot validation, API routing, or product workflow rules.

## Affected Backend Pieces and Grep Evidence

- The real `POST /api/v1/disbursements/<id>/mark-transfer-successful/` endpoint and the disbursement
  workflow validation are exercised, but their behavior is not changed: rejecting transfer evidence
  dated before CFC authorisation is the correct production contract.
- The guarded `seed_epic_009_e2e_fixture` command remains the deterministic fixture owner. No model,
  migration, endpoint, service, selector, permission, or seed behavior is changed by this repair.
- The retained server log proves the authorisation POST returned 200 immediately before the transfer
  POST returned 400 on the timestamp ordering field, so the backend is a consumer used for regression
  evidence rather than an implementation target.

## Affected Frontend and Browser Pieces

- `sfpcl-lms/e2e/epic-009-staff-disbursement-closure.e2e.spec.ts` is the only expected code change.
  It owns the real-Django request sequence and the nine screenshot assertions/manifests.
- Production `LoanAccount360`, `DisbursementHub`, `PaymentAuthorisationHub`, routes, API clients,
  authentication, and styles are not changed.

## Blast Radius and Other Consumers

- Senior Finance transfer execution, CFC authorisation, Loan Account activation, advice availability,
  SAP posting, notifications, and MP14 portal evidence remain governed by existing backend owners.
- Other Playwright specs share the configured Django/Vite servers but do not consume this spec's
  transfer timestamp value.
- Ralph still deletes/recreates the declared screenshots and validates exactly nine distinct SHA-256
  entries independently in each of two trusted runs. Existing 009I2 evidence remains untouched.

## Regression Plan by Affected Module

- Browser contract: use the declared Playwright spec as the regression test at the real request seam.
  First preserve the retained red output proving the ordering failure, then update only its transfer
  timestamp derivation and run Playwright collection plus the trusted spec when Chromium is available.
- Backend workflow: do not add or weaken a backend test because the demonstrated rejection is correct
  and no backend code changes. The trusted browser run itself re-exercises the real endpoint and must
  receive a successful envelope after supplying valid chronological evidence.
- Frontend production modules: rerun the focused Loan Account 360, Disbursement Hub, and Payment
  Authorisation Hub tests, followed by typecheck, lint, and build. No new component regression is
  required because no production component changes.

## Frontend Design Rules

No UI code, labels, styling, colours, typography, spacing, layout, cards, badges, tables, or components
change. The repair changes only test evidence timing at the real API boundary.
