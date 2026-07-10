# Risk Assessment

Risk level: High — completed under the owner's standing approval; no 006E3 veto exists.

- Selected slice: 006E3-appraisal-history-and-review-authority-hardening
- Mode: normal_run
- Data migration: one additive migration creates review history, conservatively downgrades unproven
  provenance, and backfills only complete latest-known legacy reviews.
- Security/authority: review now requires the exact permission and active `credit_manager` role;
  tests distinguish role/permission denial from object-scope denial and assert zero denied writes.
- Sensitive data: comments remain only in appraisal-owned history; generic audit/workflow evidence
  contains decision IDs and metadata but no comments, detailed rejection reason, or frozen free text.
- Transactionality: history, appraisal state, optional rejection note, audit, and workflow evidence
  share the existing atomic review boundary; forced-failure tests prove rollback.
- Reversibility: schema/history backfill reverses by dropping the derived table. Conservative
  provenance downgrades intentionally remain because relabelling unproven rows as verified is unsafe.
- Residual risk: PostgreSQL competing-transaction proof and lock-order normalization remain owned by
  006F3 and are mandatory there; the two default-suite skips are unchanged and not evidence for 006F3.
- Diff limits: one migration, no dependencies, no protected/source changes, below file/line caps.
