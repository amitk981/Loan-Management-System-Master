# Risk Assessment

Risk level: High (slice-declared persistence, delivery-idempotency, and borrower-disclosure risk).

- Exactly one communications migration changes existing provenance classification and makes four
  template-provenance fields nullable. It does not delete outboxes, attempts, receipts,
  Communications, actions, audits, workflows, jobs, capabilities, rendered advice, or provider
  evidence.
- Deterministic 0005 attempts become `legacy_0005`; attempt-less, mixed, or checksum-incoherent
  rows become `ambiguous_legacy`. Both are `legacy_partial`, have reconstructed template facts
  cleared, and remain permanently outside current replay/portal/download truth.
- Only a non-legacy provider attempt with a complete internally checksummed snapshot becomes
  `frozen_before_dispatch/verified`. Database constraints bind origin, status, and the full-versus-
  null provenance shape; runtime independently checks the frozen checksum, accepted-attempt
  identity/digest, and terminal chain.
- Reverse refuses before removing the origin marker when partial rows exist. Clean verified state
  reverses/reapplies unchanged. This is intentionally fail-closed and can block a rollback rather
  than misrepresent history.
- Public replay and portal/download refusal were exercised with zero provider calls and retained
  row/Communication counts. Both PostgreSQL five-caller methods passed twice with one provider
  identity and one terminal winner per race.
- Residual risk: a privileged database writer can rewrite an entire evidence chain; that is treated
  as wholesale database tampering, not an application-supported provenance transition. Provider
  transport remains governed by later H7/H8 slices.
- No frontend, API wire, permission, money, account, disbursement, external-provider, dependency,
  or protected/source-document change was made.
