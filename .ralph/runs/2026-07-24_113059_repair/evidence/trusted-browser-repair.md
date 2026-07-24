# Trusted Browser Repair Evidence

## Failing signal

The first independent trusted run launched Chrome and executed all four declared 012E scenarios.
Populated, empty, and forbidden passed. The error-state scenario failed before capture because
`staffLogin` used this non-exact shell-readiness locator:

`getByRole('button', { name: 'Dashboard' })`

Once the error state rendered `Refresh dashboard`, Playwright strict mode resolved that locator to
both the sidebar `Dashboard` button and the `Refresh dashboard` button. The retained raw output is
`terminal-logs/trusted-browser-red.log`.

## Minimal repair

`sfpcl-lms/e2e/helpers.ts` now asks for the exact accessible name:

`getByRole('button', { name: 'Dashboard', exact: true })`

This changes only the shared E2E login readiness assertion. It does not change application code,
browser configuration, runtime behaviour, screenshots, business rules, or permissions.

## Focused checks

- `terminal-logs/playwright-spec-list-green.log`: Playwright loads the repaired config/spec and
  discovers the exact four declared scenarios successfully.
- `terminal-logs/browser-infrastructure-probe.log`: the repair run's trusted preflight launched the
  centrally selected Chrome and created a page successfully.
- `terminal-logs/agent-sandbox-browser-recheck.log`: a direct rerun from the coding-agent sandbox
  aborts Chrome at macOS application registration before page creation. This is the documented
  sandbox boundary, not a product assertion failure, and produced no screenshots.

Full independent repair validation must rerun the exact trusted command outside the coding-agent
sandbox twice and verify all four PNG manifests before the candidate can be committed.
