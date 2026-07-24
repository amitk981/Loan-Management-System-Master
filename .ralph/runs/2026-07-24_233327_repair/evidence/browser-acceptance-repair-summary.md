# Trusted Browser Repair Summary

## Demonstrated validator failure

The authoritative first trusted-browser run from
`.ralph/runs/2026-07-24_225638_normal_run/evidence/terminal-logs/trusted-browser-acceptance-1.log`
launched Chromium, rendered S56, and failed at line 68 because
`getByText('Browser Committee Approver')` resolved to two elements in Playwright strict mode.

Inspection confirmed that the two occurrences are required product evidence:

1. the approver named under `Required approval authority`; and
2. the same approver's terminal action under `Recorded approval decisions`.

The CFO name is rendered through the same two evidence paths and would have exposed the next
same-domain strict-locator error.

## Repair

The E2E contract now uses `toHaveCount(2)` for both named approvers. This asserts that both required
authority and recorded action evidence render, while removing the ambiguous strict-mode
`toBeVisible()` locator. No product component, API, backend, styling, or source document changed in
this repair turn.

## Local validation

- `browser-spec-list.log`: PASS, exactly one declared Playwright test discovered.
- `frontend-focused.log`: PASS, 11/11 DefaultRecoveryHub tests.
- `frontend-static-gates.log`: PASS, typecheck, lint, and build.
- `browser-contract-static.log`: PASS, trusted-browser spec/screenshot declaration.
- `git diff --check`: PASS.

The exact browser command was retried after the repair, but the coding sandbox's system Chrome
process exited during launch before the test body. The log is
`terminal-logs/trusted-browser-green-attempt-1.log`. This is the known macOS sandbox boundary, not
a product assertion result. No PNG or manifest was fabricated.

Independent trusted validation must now run the declared spec twice and retain a structurally valid
`recovery-approval-decision.png` plus manifest for each isolated run.
