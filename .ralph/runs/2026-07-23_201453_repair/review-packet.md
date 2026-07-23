# Review Packet: 2026-07-23_201453_repair

## Result
Ready for independent validation

## Slice

`011NA-member-portal-notices-grievances-and-notifications`

## Demonstrated failure

The prior trusted validator successfully logged into the member portal and rendered
`LN-PORTAL-CLOSED-001`, then failed at the exact lowercase `issued` assertion. The closure page uses
the shared `StatusBadge`, which intentionally converts transport values to borrower-facing title
case. Static continuation through the same spec exposed the equivalent lowercase `read` mismatch
and an unsupported grievance category value.

## Repair

- Changed exact visible status assertions from `issued`, `released`, and `read` to `Issued`,
  `Released`, and `Read`.
- Changed the grievance option and mocked response from unsupported `repayment` to the canonical
  `repayment_adjustment_issue`.
- Preserved the product candidate, real portal login, own-scope/foreign-value checks, notification
  POST assertion, grievance POST assertion, 390×844 viewport, and exact required screenshot name.

## Diagnosis

Correct hypothesis: the acceptance test compared raw transport values against title-cased visible
labels and used a category absent from the bounded model/UI/API vocabulary. The API route, closure
projection, page routing, and mobile rendering were not the cause: the failed validator had already
proved the closure row was present.

## Validation

- Exact Playwright spec collection: 1 test collected.
- Focused portal communications Vitest file: 5 passed.
- TypeScript typecheck: passed.
- ESLint: passed.
- Production build: passed.
- Diff whitespace check: passed.
- Exact Playwright execution from the agent sandbox: Chrome exited before page creation. The
  orchestrator preflight browser probe passed; no screenshot was fabricated.

Evidence:

- Prior red-capable validator:
  `.ralph/runs/2026-07-23_192235_normal_run/evidence/terminal-logs/trusted-browser-acceptance-1.log`
- Repair collection and gates: `evidence/terminal-logs/member-portal-communications-collection.log`,
  `frontend-portal-communications-focused.log`, `frontend-typecheck.log`, `frontend-lint.log`, and
  `frontend-build.log`
- Sandbox browser infrastructure result:
  `evidence/terminal-logs/member-portal-communications-e2e-run-1.log`

## Substantive risk

Independent validation must execute the exact trusted-browser contract twice and produce the
declared mobile screenshot. If Chrome launches and a new assertion fails, it belongs to this same
bounded browser-validator domain and must be repaired before commit.

## Recommended Next Action

Run full independent validation. Commit only after both trusted browser executions pass and their
screenshot manifests are complete.
