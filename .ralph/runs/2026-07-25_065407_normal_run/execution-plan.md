# Execution Plan

Selected slice: 012DAC-audit-explorer-and-observation-frontend-wiring

## Scope and constraints

- Wire S74 Audit Log Explorer and the separate immutable auditor-observation flow to the existing
  012D/012D2 interfaces only.
- Reuse the approved prototype shell, table, detail, modal/form, alert, and state patterns without
  introducing a new visual system.
- Keep backend scope and permission responses authoritative; never issue audit-log mutations or
  render restricted/raw sensitive audit fields.
- Remove owned audit/observation runtime fixtures without changing reports/export behavior from
  012DAA/012DAB.
- Modify only permitted frontend, test, run-evidence, and working-document paths. Do not modify
  source documents, protected workflow files, orchestrator-owned state/progress, slice status, or
  mechanical handoff facts.

## Behavior-first implementation

1. Inspect the existing 012D/012D2 frontend transport contracts, AuditArchiveHub prototype,
   routing/navigation, prior reports/export browser spec, and nearby frontend test/state patterns.
2. Add one failing frontend behavior test for the audit request/filter/pagination interface, save
   RED output, implement the smallest green explorer wiring, and save GREEN output.
3. Repeat vertical red→green cycles for read-only/restricted-field behavior, explorer states,
   auditor-only observation creation, immutable observation revisit, and denial/no-leakage states.
4. Extend the trusted browser spec without removing prior 012DAA/012DAB coverage; produce all five
   required screenshots in two passing runs.
5. Run focused frontend tests throughout, then impacted tests, typecheck, lint, and build. Run cheap
   backend checks only if appropriate; leave the authoritative complete/impacted backend lane to
   the orchestrator.
6. Inspect diff stats and targeted hunks, verify no mock reads or audit mutation affordances remain,
   and save terminal logs, browser evidence, risk assessment, review packet, and final summary.

## Acceptance evidence

- Request/query evidence covers entity, action, actor, date range, deterministic pagination, and
  backend-authoritative unauthorized responses.
- Rendering evidence proves restricted fields/raw sensitive values are absent and audit rows have
  no edit affordance or write path.
- Observation evidence proves scoped Internal Auditor create/revisit behavior and truthful
  validation, foreign-evidence, lifecycle/edit, and role denials.
- Two trusted browser runs retain `report-results.png`, `export-job-status.png`,
  `masked-export.png`, `audit-explorer.png`, and `audit-observation-recorded.png`.
- Final review packet contains source→code→test traceability and the exact result
  `Ready for independent validation`.
