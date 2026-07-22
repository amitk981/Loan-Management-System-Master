# Risk Assessment

Risk level: High

- Selected slice: 011E-recovery-decision-approval
- Mode: normal_run
- Manual review required: independent Ralph validation is required before commit/merge.

## Risk Analysis

- Authority and permissions: the critical write requires `recovery.decision.create`, an actor who
  belongs to the frozen configured route, and that actor's retained approved action. Recovery
  approval itself reuses the existing approval owner, version checks, object attribution,
  maker-checker exclusions, and distinct configured authorities. No role is granted the critical
  decision permission by default.
- Business-policy ambiguity: no Sanction Committee/Board choice, amount threshold, or configured
  other-action executor was invented. The route resolves one effective action-specific recovery
  matrix rule. Unsupported Board-as-record and non-joint routes fail closed; A-158 records the
  open governance boundary.
- Data integrity: one-to-one database constraints bind one immutable decision to the default, note,
  approval case, and workflow event. The domain writer locks the default, note, and approval case;
  exact replay returns retained truth and changed replay conflicts.
- Concurrency: the exact declared PostgreSQL five-request acceptance passed with one record, audit,
  and event chain. Independent validation will execute the declared class twice in isolated
  databases.
- Stale/forged evidence: decision creation cross-checks the default state, note link/status/action,
  approval case type/link/status/time, current protected matrix identity/version/action, frozen
  projection, complete distinct approvals, role codes, and action chronology. Unknown client fields
  and client-supplied status are rejected before writes.
- Auditability: approval actions and the recovery decision each write their own immutable audit and
  workflow evidence. The decision retains exact matrix, authority, and approval-action identities;
  mutable current roles are not used as terminal proof.
- Migration: one new recovery migration creates the protected decision table and constraints.
  Django check and migration-sync pass; test database creation exercised the migration on SQLite
  and PostgreSQL.
- Reverse-consumer risk: the shared approval availability projection was corrected to disable
  already-acted/conflicted actors. The 145-test focused approval/matrix/recovery pack passed,
  including the 011D Non-Payment Note reverse consumer.

## Residual Risk

- Production remains fail-closed until governance provisions an effective recovery matrix rule and
  explicitly grants `recovery.decision.create` to the configured decision path.
- Board-only/both authority as a non-login approval record and execution of configured “other”
  actions remain intentionally unresolved. 011F owns execution and must consume only the retained
  executable action projection.
- The complete High-risk backend suite and coverage floor are intentionally not run by this agent;
  the orchestrator owns that authoritative lane.

No protected file was modified. Candidate size is at the configured boundary of 30 files and below
the 2,000-line limit; redundant evidence logs were consolidated without losing RED/GREEN commands or
results.
