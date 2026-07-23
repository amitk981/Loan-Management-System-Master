# Review Packet: 2026-07-23_214956_repair

## Result
Ready for independent validation

## Slice
011O-auditor-read-only-views

## Repair finding

The candidate’s product behavior was not the cause of the saved browser failures. The E2E contract
mistook existing read-only navigation/dismiss controls for operational actions, and its shared helper
required a success heading in the intentionally heading-free unauthorised state.

## Repair completed

- Kept the populated scenario’s network-level assertion that no API POST/PATCH/DELETE occurs.
- Replaced the over-broad substring button matcher with exact Epic 011 operational action labels.
- Required `Epic 011 Audit View` only for successful populated and empty responses.
- Allowed the denied-read scenario to assert the existing `Auditor access is not authorised.` card.
- Changed no product code, backend authority, role scope, schema, dependency, or visual styling.

## Source-to-code traceability

- `docs/source/auth-permissions.md` §15.11 and §26.7 say the Internal Auditor is read-only across
  default/recovery/closure records; the Playwright populated scenario asserts no operational action
  labels and records every attempted API mutation, verified by
  `e2e/auditor-read-only-epic-011.e2e.spec.ts`.
- `docs/source/auth-permissions.md` §23 requires graceful `403` handling; the repaired denied-read
  scenario now verifies the explicit unauthorised card instead of incorrectly requiring the success
  heading.
- `docs/source/design-system.md` §36.6 emphasizes read-only evidence/audit views; the repair changes
  test targeting only and leaves the approved UI intact.

## Evidence

- `evidence/terminal-logs/auditor-epic-011-trusted-functional-red.log`: preserved trusted functional
  red run showing the two repaired browser-contract failures after Chromium launched.
- `evidence/terminal-logs/auditor-epic-011-browser-red.log`: local exact command blocked at Chrome
  launch before page creation.
- `evidence/terminal-logs/auditor-epic-011-frontend-focused.log`: 4 focused tests passed.
- `evidence/terminal-logs/auditor-epic-011-playwright-list.log`: all 3 declared scenarios discovered.
- `evidence/terminal-logs/frontend-typecheck.log`: passed.
- `evidence/terminal-logs/frontend-lint.log`: passed.
- `evidence/terminal-logs/frontend-build.log`: passed.
- `evidence/terminal-logs/auditor-epic-011-browser-final-attempt.log`: final local exact rerun was
  again blocked by system Chrome `SIGABRT` before page creation.
- `evidence/terminal-logs/browser-infrastructure-probe.log`: orchestrator-owned preflight probe passed.

## Independent validation boundary

The exact trusted Playwright command and both screenshot manifests remain authoritative. The agent
sandbox cannot launch Chrome, while the orchestrator-owned probe can; therefore the orchestrator must
run the repaired three-scenario spec, generate the populated/empty/unauthorised screenshots twice,
and reject the candidate if any newly exposed error remains.

## Recommended Next Action

Run full independent validation of the preserved candidate. Commit only if the trusted browser
contract, exact screenshots/manifests, and all subsequently selected gates pass.
