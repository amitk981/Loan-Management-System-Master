# Risk Assessment

Risk level: High

- Selected slice: 009E3-disbursement-amount-and-source-bank-governance-closure
- Mode: normal_run
- Standing approval: applies; no owner veto is recorded for this slice.
- Manual review required: orchestrator independent validation and normal High-risk review.

## Material risks and controls

- Money boundary: lesser amounts could accidentally permit over-sanction or funded-account writes.
  Controls: positive 18,2 validation, both immutable-terms and sanction caps, zero-balance/status
  reconciliation, exact replay digest, CFC approval of the frozen amount, and boundary tests.
- Configuration integrity: a current source account could exist with partial or rewritten history.
  Controls: database-required activation proof, append-only predecessor/deactivation relations,
  exact version/audit sibling reconciliation, closed effective range, and fail-closed resolution.
- Concurrency: simultaneous first activation/replacement could retain multiple winners or orphan
  evidence. Controls: observed-current comparison, locked Critical authority, nested atomic
  savepoint, partial unique current constraint, stable conflict conversion, and two PostgreSQL
  rounds of five first activations plus five replacements.
- Ownership drift: raw loan rows could look equivalent to lifecycle-created accounts. Controls: a
  lifecycle-owned typed decision reconciles singular status-history/audit/workflow evidence and
  freezes their ids into initiation evidence.
- Migration: existing pre-009E3 governance rows need complete retained history before constraints
  apply. Control: the single migration backfills activation/deactivation/predecessor evidence before
  installing constraints; local migration apply and migration-sync checks pass.
- Sensitive data: source-bank details must not leak through evidence. Controls: lifecycle ledgers
  retain UUIDs/digests/masked metadata only; existing encrypted bank fields remain unchanged.

## Residual risk

A-126 remains open only for governance to name the real business provisioner. The mechanism is
grantable but no role receives it by default, so production fails closed until that decision.
