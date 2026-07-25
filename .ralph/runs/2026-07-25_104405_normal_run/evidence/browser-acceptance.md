# Trusted Browser Acceptance

Declared contract:

- Spec: `e2e/deployment-smoke-readiness.e2e.spec.ts`
- Required screenshot: `deployment-smoke-readiness.png`
- Contract repetitions: two

The local preflight browser probe passed. Both focused contract attempts subsequently
started the isolated Django and Vite servers but Chrome exited during launch, before a
page or test body existed. No screenshot was fabricated.

Logs:

- `terminal-logs/browser-infrastructure-probe.log`
- `terminal-logs/deployment-smoke-browser.log`
- `terminal-logs/deployment-smoke-browser-retry.log`

Per the slice's `localhost-e2e-server` contract, trusted validation makes the
authoritative browser decision and produces the declared screenshots when Chromium is
available.
