# Risk Assessment

Risk level: High

- Selected slice: `007E-conflict-of-interest-blocking`
- Standing approval: present; no `[revoked]` entry exists.
- Primary risk: sanction authority and segregation-of-duties logic now changes who may act and can
  terminate a case without sanction creation.
- Data risk: one migration adds typed conflict declarations, cycle-level general-meeting/block
  fields, the `abstained` action decision, and a conservative maker-fact backfill. It does not
  rewrite required-approver history or prior actions.
- Permission risk: excluded actors receive only attributable limited detail/history read. They do
  not enter assigned queues, and action permissions or live committee membership do not widen
  scope.
- Financial risk: no amount, rate, loan-limit, or sanction calculation changed. Unsatisfied frozen
  authority fails closed as `blocked_by_conflict` and creates no sanction decision.
- Audit risk: COI-006 intentionally permits one denial audit after the action transaction rolls
  back. Tests prove no case/action/sanction/workflow/communication mutation accompanies that row.
- Operational risk: the initial full gate found a migration-graph dependency that interfered with
  a legacy witness migration test. Narrowing the dependency to the earliest consumed application
  schema repaired it; focused migration tests and the complete suite pass afterward.
- Residual governance question: A-082 records that authoritative person-to-user/director-relative
  capture remains owned by the future member relationship source; typed declarations feed the
  evaluator until then.
- Protected/source files: unchanged.
- Diff limits: within configured 30 files / 2,000 lines / one migration limits.
