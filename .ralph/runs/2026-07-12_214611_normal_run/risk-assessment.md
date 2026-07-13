# Risk Assessment

Risk level: High (owner standing approval; no veto recorded).

- Business-rule risk: active-member eligibility can admit/block borrowers. Controls are dated public-
  interface tests across gaps, future rows, service, institution, relaxation, and invalid evidence.
- Data risk: one additive JSON migration stores complete eligibility evidence. Legacy assessments use
  `{}`; no destructive/backfill operation occurs and migration sync is green.
- Authority risk: active verification changes member state. Permission, maker-checker, required
  reason, optimistic version/result, repeated decision, and transaction rollback are enforced before
  audit/history writes.
- Concurrency risk: the new PostgreSQL two-verifier race passed twice with one complete winner and
  zero loser evidence; the existing five credit races also passed twice.
- Privacy risk: internal snapshots retain evidence IDs for review, while PortalAccount-scoped output
  omits member IDs, staff actions, verifier facts, and cross-member records.
- Residual risk: 006Z2 must accept only a verified matching result and strip internal row/evidence
  fields from its borrower limit projection. This is sharpened in that slice.
