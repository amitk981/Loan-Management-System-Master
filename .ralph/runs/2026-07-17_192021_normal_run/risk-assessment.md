# Risk Assessment

Risk level: High

- Selected slice: 009G2-post-disbursement-register-checklist-and-replay-closure
- Mode: normal_run
- Standing approval: active; no owner veto is recorded.

## Risk Surface

- The slice changes the successful money-transfer transaction, funded loan activation evidence,
  Loan Register truth, idempotency replay, and a post-disbursement legal checklist action.
- One migration adds two protected financial ledgers, strengthens the successful-disbursement
  aggregate, and replaces Epic-008 placeholder checklist constraints with executable Epic-009
  signature/account/ready-state constraints.
- Incorrect replay or partial writes could duplicate activation, overstate register/advice truth,
  or create a checklist signature not backed by an actual transfer.

## Mitigations Verified

- Transfer, activation, register, pending advice identity, history, audit, and workflow remain in one
  locked transaction; database uniqueness and aggregate constraints reject partial success facts.
- Both new ledgers bind exact object, amount, reference digest, upload checksum, action/evidence,
  audit, and workflow identities. Current resolution fails closed on missing or changed relations.
- Exact replay returns the retained §45.2 wrapper with unchanged row/action counts; changed keys,
  payloads, actors, owner evidence, register facts, and advice facts conflict without writes.
- The existing top-level checklist process coordinator injects a frozen Finance decision into the
  legal owner, so no legal-to-disbursement dependency was introduced.
- Checklist signing requires active authentication, explicit grant, effective Senior Finance role,
  exact initiating-maker scope, current transfer evidence, and the complete prior approval stage.
  The signature/action/account/ready status/audit/workflow/version update is atomic and constrained.
- Independent standards/spec review found aggregate and dependency issues in the first draft; both
  were corrected and the spec re-review reported no remaining fidelity issue.

## Residual Risk

- PostgreSQL lock/race behavior cannot be executed in the local SQLite lane. Two five-caller methods
  collect successfully and the declared capability delegates authoritative twice-run execution to
  the orchestrator.
- Advice delivery remains deliberately absent. The stable intent permits only pending/sent states;
  009H2 must supply current provider/contact/rendered-content evidence before changing delivery.
- The orchestrator still owns complete backend coverage/floor, protected-path, queue, migration,
  and PostgreSQL acceptance before commit/merge.
