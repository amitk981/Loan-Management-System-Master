# Review Packet: 2026-07-15_204059_repair

## Result
Repair Complete — Independent Browser Acceptance Pending

## Slice
008L4-portal-production-boundary-and-browser-proof

## Recommended Next Action
Run the exact declared trusted-browser command twice outside the coding sandbox. Accept only if both
specs pass and all four declared screenshots are genuine and non-empty; then let Ralph commit,
merge, and push.

## Demonstrated failure and cause

- Both trusted runs logged `POST /portal/auth/login/ 200` and `GET /auth/me/ 200`, then two forbidden
  staff `/api/v1/dashboard/` calls and a timeout waiting for `Portal Contract Member`.
- The deterministic seed used `borrower_portal_user` from the canonical catalogue while that role
  was still marked future/inactive. `current_user_payload` therefore returned `roles: []`, and the
  frontend correctly mapped the role-less identity to its neutral staff shell.

## Repair review focus

- `identity.catalogue` activates only `borrower_portal_user`; all genuinely future external roles
  remain inactive and the role receives no staff permission links.
- The seed test crosses real portal login and `/auth/me` and asserts the exact borrower role payload,
  so a fixture-only browser boolean cannot hide the production identity contract again.
- The two Playwright specs, guarded fixtures, portal documentation business logic, and UI remain
  unchanged by this repair.

## Traceability and validation

- Source/slice says portal login reuses the auth foundation with the Borrower role
  (`005FA` requirement 1); catalogue now returns that active role, verified by
  `test_seed_creates_standard_role_and_team_codes` and
  `test_seed_is_idempotent_and_exposes_real_portal_contracts`.
- RED: focused tests observed catalogue `inactive` and `/auth/me roles=[]`. GREEN: both exact
  assertions pass; 25 affected identity/portal tests pass.
- Full gates: frontend lint/typecheck/build and 304 tests pass; Django check/migration drift and all
  897 backend tests pass with 46 expected skips and 91% coverage; Playwright collects the exact two
  declared specs.
- Browser acceptance remains external because local Chromium cannot acquire its macOS Mach port and
  the in-app browser exposes no backend. No screenshot was fabricated.
