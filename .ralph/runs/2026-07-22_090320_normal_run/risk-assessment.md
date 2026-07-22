# Risk Assessment

Risk level: Medium (slice-declared); independent validation is expected to classify the schema and
routing change into its authoritative backend lane.

- Selected slice: 011A-default-case-opening
- Mode: normal_run
- Manual review required: independent Ralph validation and review remain required before commit.

## Material risks and controls

- Financial-truth risk: a caller could falsely claim default. Control: the public request has no
  paid/missed field; `DefaultWorkflow` consumes the loan-owned, locked schedule/allocation decision.
  A real repayment-allocation integration test proves a fully allocated principal line cannot open.
- Duplicate/race risk: two detections could create parallel cases/evidence. Control: the loan row is
  locked, the missed schedule obligation has a database unique constraint, replay returns the
  retained case, and the authoritative PostgreSQL two-client race creates one case/audit/event.
- Authority/nondisclosure risk: default information could cross member/loan scope. Control: opening
  requires both the exact permission and active Credit Manager role; reads derive Credit/CS scope,
  persisted required-approver identity, or an active Auditor scope grant. Guessed/inaccessible
  identities return nondisclosing 404 responses; Auditor mutation is explicitly denied.
- Audit-integrity risk: a case could exist without transition evidence. Control: case, safe audit,
  and canonical workflow event are created atomically; replay and rejection tests assert evidence
  counts remain one or zero as appropriate.
- Date risk: adding three calendar months differs from adding a fixed number of days. Control: the
  workflow performs bounded calendar-month arithmetic from the persisted scheduled due date.
- Migration risk: the slice adds one initial migration with model constraints and role read grants.
  Model/migration sync and isolated forward/reverse/reapply proof are green.

## Scope and residual risk

- No frontend, expiry/assessment, extension, recovery, or repayment-rule changes were made.
- No new dependency was added and no assumption entry was needed; the selected source sections
  resolve the trigger, grace interval, authority, API paths, statuses, and audit requirement.
- The orchestrator must still run the one authoritative impacted/full backend lane selected from
  the final changed paths. The agent intentionally did not run the complete suite or coverage.
