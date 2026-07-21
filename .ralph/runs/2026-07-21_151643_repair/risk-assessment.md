# Risk Assessment

Risk level: High

- Selected slice: CR-015-epic-010-terminal-servicing-owner-finalizer
- Mode: repair
- Demonstrated risk: broadening exact replay in the shared SAP-posting owner changed a legacy
  financial endpoint from duplicate conflict to success. A second PostgreSQL signal exposed a
  reminder-worker claim gap where a concurrent loser could observe `running` before terminal truth.
- Financial mitigation: exact SAP replay is now an explicit privilege of the composite command;
  legacy posting retains `409`, and exact command retries still compare the retained SAP facts.
- Concurrency mitigation: the monitoring owner serializes reminder job execution across claim,
  current-source proof, provider effect, provider evidence, and terminal job state. Non-reminder
  communication jobs retain the existing communications-owned execution path.
- Evidence: the exact financial regression is RED/GREEN; 6 direct-repayment regressions, 65
  communications/reverse-owner regressions, and the five-case PostgreSQL class twice are green.
- Database/schema risk: no additional model or migration change was introduced by this repair;
  migration consistency and Django system checks pass.
- Residual risk: the orchestrator must still run the authoritative complete suite and coverage lane.
- Manual review required: no; independent Ralph validation remains required before commit.
