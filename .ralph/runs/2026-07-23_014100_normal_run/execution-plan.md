# Execution Plan — 011K Compliance Control Tracker Foundation

## Boundary

Implement only the backend compliance foundation described by slice 011K. Add the compliance owner,
its persistence, task engine, HTTP endpoints, catalogue seed, audit/notification/job integration, and
the declared PostgreSQL race acceptance. Do not add frontend work or the 011L/011M/011N trackers.

## Public module interface

Keep frequency, ownership, due/overdue state, escalation, evidence rules, and audit behind
`ComplianceTaskEngine`. HTTP views and scheduled execution call this same interface. Existing
documents, scheduler, communications, audit, stamp/notary, recovery, and archive modules remain the
owners of their facts; compliance stores references and review facts only.

## TDD tracer bullets

1. RED/GREEN: generating due tasks creates exactly one task per active control/period with the
   configured owner, reviewer, due date, and due/overdue status; exact replay is idempotent.
2. RED/GREEN: monthly, quarterly, annual, and ongoing controls derive stable periods and reject
   invalid/disabled/missing configuration without partial writes; concurrent generation is unique.
3. RED/GREEN: evidence submission requires a matching governed document and valid task state;
   review enforces authorised distinct maker/checker, rejection history, accepted immutability, and
   no premature task close.
4. RED/GREEN: control/task GET/POST/PATCH and evidence submit/review endpoints enforce the canonical
   permissions, standard envelopes/filters, and truthful `available_actions`.
5. RED/GREEN: annual money-lending review requires restricted legal opinion and Board note, links
   the matching annual task/evidence, records CS review facts, and remains unique by year/state.
6. RED/GREEN: overdue generation queues one replay-safe notification/escalation and records a
   scheduler run with partial-failure detail rather than fabricating compliance.
7. Add the exact PostgreSQL acceptance class and verify concurrent scheduler execution creates one
   task/notification per control/period.

## Verification and evidence

- Save every focused RED and GREEN command/output under `evidence/terminal-logs/`.
- Run focused compliance tests after each tracer bullet.
- Run Django check and migration-sync check with the mandated Ralph virtualenv interpreter.
- Run only focused/impacted backend tests locally; leave authoritative impacted/full coverage and
  PostgreSQL capability validation to the orchestrator.
- Save API examples, permission/maker-checker matrix, cross-owner read-only probes, risk assessment,
  and review packet. Finish with review-packet Result exactly `Ready for independent validation`.

## Permissions and protected paths

Edits are limited to `sfpcl_credit/**`, `docs/working/**`, and this run's `.ralph/runs/**` evidence,
all allowed by `.ralph/permissions.json`. Do not edit protected workflow files, orchestrator-owned
state/progress/changed-files/slice-status facts, or any `docs/source/**` material.
