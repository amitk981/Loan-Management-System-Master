# Execution Plan

Selected slice: 011PB-recovery-decision-frontend-wiring

## Scope

Complete only the S56 recovery-decision wiring in the existing Default/Recovery Hub and gate the
already-delivered S57 execution controls exclusively from canonical backend projections. Remove the
page's remaining mock/inline business fixtures without changing the approved visual system.

## Permission Check

- Allowed product scope: `sfpcl-lms/src/**`, the slice-owned E2E spec under `sfpcl-lms/e2e/**`,
  the existing recovery/default backend modules and focused test needed to preserve server-owned
  action authority, `docs/working/API_CONTRACTS.md`, and run evidence under
  `.ralph/runs/2026-07-24_225638_normal_run/**`.
- Protected and forbidden paths will not be edited, including `docs/source/**`,
  `docs/working/FRONTEND_DESIGN_RULES.md`, `.ralph/config.yaml`, `.ralph/permissions.json`,
  scripts, workflow policy, and Git metadata.
- Ralph-owned mechanical files and slice status will not be edited.

## Implementation Sequence

1. Inspect the existing Default/Recovery Hub, shared Epic 011 staff API seam, focused tests, and the
   trusted-browser scenario to identify the delivered S53-S55 and S57 contracts.
2. Add failing focused frontend tests for recovery-decision request/action/canonical-refetch,
   mandatory reason, exact blocked states, server-owned action visibility, and final mock removal.
3. Extend the shared API types/functions only as needed for the existing 011E recovery-decision
   read/action contract.
4. Wire S56 into the existing page using only existing cards, badges, alerts, forms, and action
   patterns. Treat `available_actions`, decision state, authority/conflict evidence, and blockers as
   server-owned truth.
5. Extend the trusted-browser scenario for S56/S57 and save the required
   `recovery-approval-decision.png` evidence from two passing runs.
6. Run focused tests during implementation, then the impacted frontend test set, typecheck, lint,
   and build. Save self-contained command output under `evidence/terminal-logs/`.
7. Inspect targeted diff hunks and stats, complete risk and review evidence, and leave the review
   result exactly `Ready for independent validation`.

## Review Amendment

Independent review found that an exact frontend blocker could not truthfully reconstruct every
backend approval invariant. A focused backend RED/GREEN behavior was therefore added before the
final gates: default detail now projects `recovery_decision_control` through the existing 011E write
validator, and S56 consumes that projection for action visibility and payload identity. The response
contract was recorded in `docs/working/API_CONTRACTS.md`. Both independent re-reviews then reported
no remaining findings.

## Stop Conditions

Stop only for a protected/forbidden edit, a never-do decision, a repeated gate failure after one
focused repair, unsafe repository state, or the configured diff/file limit.
