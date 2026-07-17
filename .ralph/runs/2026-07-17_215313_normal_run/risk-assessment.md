# Risk Assessment

Risk level: High

- Selected slice: 009G3-post-transfer-aggregate-and-checklist-integrity-closure
- Mode: normal_run
- Manual review required: yes; independent Ralph validation is required before commit.

## Why this is High risk

- The slice changes a financial-success aggregate and its database constraints. A defective owner
  relation could present a disbursement as successfully registered without durable Loan Register
  evidence, or could reject a valid transfer after funds have been recorded.
- The slice changes Stage-5 Senior Manager Finance scope for the post-disbursement checklist. A
  scope defect could grant a financial sign-off to an inactive, stale, permission-only, role-only,
  cross-loan, or CFC actor, or deny the current authorised assignee.
- The slice reconciles immutable checklist action, audit, workflow, version, transfer, register, and
  advice evidence. Partial reconciliation could accept altered or duplicate evidence on replay.
- Transfer and checklist mutations are concurrency-sensitive and require the declared PostgreSQL
  five-race acceptance gate.

## Controls and blast radius

- Scope is limited to the disbursements aggregate, transfer-success and post-transfer evidence
  owners, their focused backend tests, and at most one disbursements-owned migration.
- The existing public transfer and checklist mutation interfaces and API response shapes remain the
  boundary; no frontend, dependency, external-service, or real-data change is intended.
- Database protection/constraints, zero-write conflict tests, authority-denial tests, exact replay
  mutation tests, focused Django checks, migration sync, and PostgreSQL races are the primary
  controls. The orchestrator performs the authoritative full-suite coverage and validation gates.

## Residual risk

- Legacy successful rows can be linked only when their retained register evidence is singular and
  coherent; ambiguous legacy data must fail closed rather than receive fabricated completion truth.
- Any incomplete migration, ledger reconciliation, or race coverage must fail independent
  validation. No commit, merge, or push is permitted until those gates pass.
