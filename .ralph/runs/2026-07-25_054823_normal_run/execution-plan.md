# Execution Plan — 012DAB Report and Register Export Frontend Wiring

## Scope

Implement only the prepared 012DAB frontend slice:

- connect `ReportsMIS.tsx` and `RegistersHub.tsx` export actions to the existing 012B/012C
  request, status, and audited-download API contracts;
- preserve backend job identity and backend-authoritative permission, masking, state, and expiry
  outcomes;
- remove the two screens' remaining `mockData` imports and inline business fixtures;
- cover loading, empty, error, unauthorised, validation, queued, running, failed, ready, and
  download outcomes with existing visual patterns;
- implement and run the declared trusted browser spec twice, retaining
  `export-job-status.png` and `masked-export.png`.

Out of scope: report result wiring already owned by 012DAA, Audit Log Explorer, new report
definitions, backend contract changes, operational dashboard hardening, and unrelated mock cleanup.

## Permission Check

- Product edits are restricted to allowed frontend paths under `sfpcl-lms/`.
- Evidence edits are restricted to
  `.ralph/runs/2026-07-25_054823_normal_run/`.
- `docs/source/`, protected workflow/configuration files, state/progress, slice status, mechanical
  handoff text, and Git metadata will not be modified.
- No dependency installation, Git staging, commit, merge, or push will be attempted.

## Implementation Sequence

1. Inspect the two owned screens, existing report wiring, export API client/types, permission
   utilities, status/alert/table patterns, focused tests, and the established Playwright harness.
2. Add focused frontend behavior tests first and save the failing output for export permission
   denial, job identity/state transitions, masking, and audited-download gating.
3. Implement the smallest shared export client/state seam needed by both screens, reusing existing
   components and styling only.
4. Remove owned mock reads/fixtures and add a regression assertion preventing their return.
5. Run focused tests to green and save output; repair only failures caused by this slice.
6. Implement the exact trusted browser spec and screenshots, run it twice, and retain truthful
   visual evidence.
7. Run impacted frontend tests, typecheck, lint, and build. Run only cheap backend consistency
   checks if appropriate; leave the authoritative backend lane to the orchestrator.
8. Review targeted diffs against the slice and source contracts, then write risk assessment,
   review packet, and final summary. Set the review-packet Result exactly to
   `Ready for independent validation`.

## Evidence Plan

- `evidence/terminal-logs/frontend-export-red.log`
- `evidence/terminal-logs/frontend-export-green.log`
- focused test, typecheck, lint, and build logs
- two-run browser logs plus `export-job-status.png` and `masked-export.png`
- masking, rejection, audited-download, and transition summaries in the review packet

