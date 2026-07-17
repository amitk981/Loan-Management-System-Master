# Risk Assessment

Risk level: High

- Selected slice: 009D4-readiness-effective-role-and-signature-scope-closure
- Mode: normal_run
- Standing approval: confirmed; no veto is recorded.
- Manual review required: independent Ralph validation before commit/merge.

## Security and business risk

- The change affects authorization for a financial readiness read. The principal risk is widening
  object access when an actor has multiple primary/governed roles. Mitigation: the explicit
  permission remains mandatory; only active central effective roles participate; each source role
  keeps its own canonical scope; the result is an OR of independently bounded scopes; unknown or
  inactive authority and permission-only actors are denied.
- The change affects a legal-document blocker. The principal risk is ignoring adverse signature
  evidence. Mitigation: only unrelated or superseded document history is excluded. Every signature
  on each latest current applicable required document remains subject to exact party identity,
  signer-set, current mismatch-resolution, audit, version, workflow, renderer, and approval-owner
  reconciliation.
- No write path, schema, migration, route, response envelope, permission seed, frontend, external
  integration, money movement, balance, task, communication, or audit-writing behavior changed.

## Regression controls

- RED/GREEN evidence reproduces the governed CFO denial and unrelated-signature poisoning defects.
- Governed CFC is tested before and after a genuine initiated-disbursement relation; a multi-role
  Senior Finance/CFC test proves union behavior when only CFC scope passes.
- All five required current document families reject an extra/wrong semantic duplicate signer.
- Existing cross-object, archived Credit, pre-initiation CFC, source reader, 23-check order,
  zero-write, secret-redaction, and query-bound tests pass.
- The orchestrator still owns the authoritative complete backend suite and coverage gate.
