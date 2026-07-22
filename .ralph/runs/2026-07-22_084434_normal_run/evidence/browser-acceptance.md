# Trusted Browser Acceptance

Exact spec implemented: `sfpcl-lms/e2e/header-notifications.e2e.spec.ts`.

The spec deterministically verifies the populated, empty, and API-error dropdown states, asserts
`read_status=unread` and `page_size=4`, and writes these exact outputs when Chromium opens:

- `header-notifications-populated.png`
- `header-notifications-empty.png`
- `header-notifications-error.png`

Two local contract attempts reached healthy Django and Vite servers but the configured system
Chrome process aborted before a page was created. No screenshot was fabricated. Full diagnostics
are retained in `terminal-logs/header-notifications-e2e-run-1.log` and
`terminal-logs/header-notifications-e2e-run-2.log`. The pre-agent central probe had passed and is
retained in `terminal-logs/browser-infrastructure-probe.log`; a later probe reproduced the transient
launch abort. Per the slice contract, independent trusted validation owns the browser acceptance
decision and must rerun this exact spec.
