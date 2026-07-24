# Trusted Browser Acceptance

Spec: `e2e/default-closure-compliance-staff.e2e.spec.ts`

Required screenshot: `recovery-approval-decision.png`

## Local attempts

The test was listed successfully with Playwright, confirming the trusted spec is syntactically
discoverable. Two execution attempts reached the isolated localhost Django readiness endpoint, then
failed before the test body because the configured system Chrome process exited during launch.

- Headless attempt: `evidence/terminal-logs/browser-contract-run-1.log`
- Headed retry: `evidence/terminal-logs/browser-contract-run-2.log`
- Root cause from Chrome: macOS sandbox denial while opening Chrome Crashpad state under the user
  Library, followed by browser process termination.

No screenshot was created or substituted. Per the slice instruction, browser acceptance remains for
the orchestrator's trusted environment and the local infrastructure failure is not treated as a
product assertion failure.
