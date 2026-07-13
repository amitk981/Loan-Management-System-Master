# Review Packet — 006Y8 Browser Repair

## Demonstrated failure

Both trusted runs successfully created and contact-corrected a witness, including a `200` PATCH and
canonical witness collection GET. Immediately after `page.reload()`, the server saw only session
restoration and dashboard requests. The app stores its selected page and application in React state
and explicitly restores authenticated sessions to `dashboard`, so the persisted contact text was no
longer mounted and the test timed out before producing screenshots.

## Narrow repair

The scenario still performs a real full reload. It then drives the visible Applications navigation,
searches for `LOE2E00601`, opens its row, and selects Witness before asserting canonical contact or
masked identity. The same helper was already used at login, so the repair adds no interception,
token injection, mock response, or alternate API path. Production routing was deliberately left
unchanged because an application-wide URL router is outside this witness slice.

## Verification

- Playwright collection: one declared Chromium test.
- Focused mounted witness tests: 4 passed.
- Frontend: build, typecheck, lint, and 176 tests passed.
- Backend: check and migration sync passed; 451 tests passed with 7 expected SQLite skips; coverage
  is 93% against the 85% floor.
- Coding-sandbox browser execution: Chromium launch denied by macOS Mach-port policy, recorded in
  `evidence/terminal-logs/browser-red.txt`; no screenshots fabricated.

## Traceability

The slice requires contact and protected identity corrections to be proven after reload through the
real routed/authenticated UI. The repaired Playwright test keeps the reload and reconstructs the
routed Application Detail through staff-visible controls before checking the canonical server data.
