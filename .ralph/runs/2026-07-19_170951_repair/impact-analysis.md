# Impact Analysis

## Demonstrated Failure

The retained trusted browser run authenticated through the real staff login and received HTTP 200
from the real `/api/v1/loan-accounts/` endpoint, but its first assertion could not find
`LN-REAL-OWNER-001`. The guarded seed creates a sanctioned account. The canonical loan-account read
owner intentionally gives Credit Managers account scope only after activation, while the assigned
Senior Finance actor can see the sanctioned account. The Playwright flow therefore selected the
wrong valid actor for the sanctioned list and summary states.

## Affected Backend Pieces

- No backend model, endpoint, serializer, permission catalogue, service, or selector behavior changes.
- `sfpcl_credit/identity/management/commands/seed_epic_009_e2e_fixture.py` remains the isolated,
  double-guarded, idempotent fixture owner. It already assigns the SAP request to Senior Finance and
  grants the existing read permission to both browser actors.
- `/api/v1/loan-accounts/` continues to use
  `sfpcl_credit/loans/modules/loan_account_read.py`: Senior Finance has current SAP-assignee scope for
  the sanctioned account; Credit Manager scope begins at active/post-transfer states.
- Regression coverage is added to `sfpcl_credit/tests/test_seed_e2e_users.py`, asserting the exact
  real-endpoint visibility boundary for the two seeded actors.

Grep evidence: `scoped_account_candidates` filters Credit Managers to active-or-later statuses and
Senior Finance to the current assigned SAP request; the fixture assigns its request to `owner.finance`.

## Affected Frontend and Browser Pieces

- `sfpcl-lms/e2e/epic-009-staff-disbursement-closure.e2e.spec.ts` is the only behavior changed. It will
  capture the sanctioned list/summary as Senior Finance, then switch through the real login form to
  Credit Manager for the active summary after the real transfer response.
- Production `LoanAccount360`, routing, API clients, staff authentication, disbursement screens, and
  payment-authorisation screens are unchanged.
- Existing `PaymentAuthorisationHub.test.tsx` coverage from the preserved implementation remains
  relevant to the terminal CFC queue refresh but is not broadened by this repair.

## Blast Radius and Other Consumers

- Loan Account list/detail consumers for Accounts Head, CFO, Company Secretary, Auditor, Credit
  Manager, Senior Finance, and CFC retain the canonical production scope matrix unchanged.
- Disbursement workspace, initiation, CFC authorisation, transfer success, advice availability,
  notifications, MP14 borrower evidence, and SAP adapters are unchanged.
- Ralph trusted-browser validation still clears and recreates all nine files twice and validates the
  per-run manifest. Existing 009I2 MP14 evidence is untouched.

## Regression Plan by Affected Module

- Backend fixture/read boundary: extend `SeedE2eUsersTests` to call the real loan-account list as both
  Senior Finance and Credit Manager and assert sanctioned visibility/absence explicitly.
- Browser contract: the declared Playwright spec itself is the correct end-to-end regression seam;
  collect it locally and rely on Ralph's two outside-sandbox executions for the authoritative browser
  green signal.
- Frontend production modules: rerun the impacted Loan Account 360, Disbursement Hub, and Payment
  Authorisation Hub tests; no new production-component regression is needed because no component is
  changed.

## Frontend Design Rules

No UI code, labels, styles, colors, typography, spacing, layouts, cards, badges, or components change.
The repair only chooses the production-authorized actor for each already-approved state.
