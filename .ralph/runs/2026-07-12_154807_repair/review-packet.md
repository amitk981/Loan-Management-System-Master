# Review Packet — 006Y8 Browser Revalidation

## Demonstrated failure

Both `2026-07-12_152923_repair` trusted runs passed witness creation, contact correction, canonical
reload/readback, and verifier-denial evidence. They then timed out at `signOut()` waiting for the
finance email, which Header renders only inside the unopened profile menu.

## Current repair state

The quarantined worktree already contains the minimal fix from `2026-07-12_153826_repair`:
`signOut()` clicks the visible `E2E Deputy Manager Finance` profile trigger, then the real Sign out
button. That exact current scenario passed twice outside the sandbox and produced all three declared
screenshots. This run therefore made no product or test-code edit.

## Verification

- Recorded red feedback: two deterministic 30-second timeouts at the impossible email locator.
- Prior outside-sandbox green feedback: the current scenario passed twice with three screenshots.
- Fresh Playwright collection: one declared Chromium test.
- Fresh coding-sandbox execution: Chromium denied before the test body by macOS Mach-port policy.
- Frontend: build, typecheck, lint, and 176 tests passed.
- Backend: check and migration sync passed; 451 tests passed with 7 expected SQLite skips; coverage
  is 94% against the 85% floor.

## Traceability

The slice requires distinct real authenticated actors for verifier denial and checker correction.
The current helper crosses that session boundary through the rendered Header menu and logout action,
without token injection, route interception, local-storage mutation, or mocked responses. The source
maker-checker requirement is implemented by backend projection/write parity and remains unchanged.

## Queue readiness

006Y9 and the next grabbable 006Z4 were inspected and already contain concrete endpoint, field,
validation, authority, concurrency, and browser requirements; no run-ahead rewrite was needed.

## Recommended next action

Run the declared browser contract twice outside the sandbox, verify the three screenshots, then
continue with 006Y9.
