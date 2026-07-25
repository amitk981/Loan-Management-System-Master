# Browser Acceptance Evidence

## Authoritative prior result

The orchestrator-owned
`.ralph/runs/2026-07-25_065407_normal_run/evidence/terminal-logs/trusted-browser-acceptance-1.log`
reached the application and identified one strict-mode failure:

- Intended exact match: the app input with accessible name `Action`.
- Unintended substring match: Playwright's injected `Block page interactions` checkbox.

The same run passed the report result, report export, masked register export, and immutable
observation scenarios.

## Repair result

The intended locator now requires the exact accessible name. Playwright contract discovery passes
and lists all five declared scenarios.

## Local infrastructure limitation

The repair sandbox's two full browser attempts and one targeted S74 attempt aborted during Chrome
launch before page creation. These are pre-page infrastructure failures, not post-launch
application assertions. They generated no screenshots, and none are claimed. The orchestrator's
separate minimal browser probe passed, so independent trusted validation remains the authority for
the complete server-backed configuration.

## Independent acceptance required

The trusted validator must run
`e2e/reports-exports-audit-explorer.e2e.spec.ts` twice and verify both complete screenshot sets:

- `report-results.png`
- `export-job-status.png`
- `masked-export.png`
- `audit-explorer.png`
- `audit-observation-recorded.png`
