# Review Packet — 006Y8 Sign-out Repair

## Demonstrated failure

Both trusted runs passed witness creation, contact correction, canonical reload/readback, and the
first two screenshots. They then timed out at `signOut()` waiting for
`e2e.credit.finance@sfpcl.example`; the third checker screenshot was never reached.

## Root cause and narrow repair

The Header's closed profile trigger displays `currentUser.name` and `currentUser.roleName`. It
displays `currentUser.email` only inside the opened profile menu. The E2E helper therefore waited
for text that could not exist until after the click it was trying to perform. It now clicks the
visible seeded name `E2E Deputy Manager Finance`, then clicks the real `Sign out` control. No direct
storage mutation, token injection, interception, mocked response, or production change was added.

## Verification

- Prior red feedback: two deterministic 30-second timeouts at the email locator.
- Playwright collection: one declared Chromium test.
- Coding-sandbox execution: Chromium launch denied before the test body by macOS Mach-port policy,
  recorded in `evidence/terminal-logs/browser-sandbox-launch.txt`.
- Frontend: build, typecheck, lint, and 176 tests passed.
- Backend: check and migration sync passed; 451 tests passed with 7 expected SQLite skips; coverage
  is 93% against the 85% floor.

## Traceability

The slice requires distinct real authenticated actors for verifier denial and checker correction.
The repaired helper uses the application's rendered account menu and logout action to cross that
session boundary, after the required canonical reload, without bypassing authentication.
