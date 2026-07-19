# Risk Assessment

Risk level: High

- Selected slice: `010C2-manual-allocation-and-financial-reversal-controls`
- Mode: `normal_run`
- Standing approval: applies; no matching owner veto was present.
- Manual review required: yes, through Ralph's independent validation and owner promotion process.

## Material risks and controls

- Financial integrity: allocation and reversal change principal, interest, schedule, and ledger truth.
  Controls are one transaction, row locks, non-negative/arithmetic constraints, exact schedule
  application records, append-only evidence, stale-state checks, and twice-passing PostgreSQL races.
- Duplicate/concurrent effects: every public financial action requires a bounded idempotency key;
  retained key/request truth is compared before writes, database uniqueness closes races, and exact
  replay returns one result. Concurrent allocation and reversal each retain one effect.
- Historical integrity: reversal never edits the original receipt/allocation/credit-ledger evidence.
  It restores from immutable per-schedule applications and appends a reversal/debit movement.
- Authority: Credit Manager and Accounts receive only source-backed capture/allocation grants.
  Manual-approval and reversal permissions are critical and default-denied under A-142/A-143; use
  additionally requires ordinary allocation authority and object scope.
- Sensitive bank data: audit JSON contains safe ids, amounts, actor/role, reason hashes, and request
  facts, not free-text reasons, narration, bank references, or SAP reference values.
- Migration: one additive migration creates correction/application evidence and constraints. It
  neither deletes nor rewrites existing financial rows; legacy allocations keep nullable new
  idempotency/approval linkage and default status snapshots.

## Residual risk

- Governance has not named the default exceptional-allocation approver or financial reverser. The
  implemented permissions therefore remain unassigned until an owner-approved role mapping exists.
- The orchestrator still owns the authoritative complete backend coverage gate and independent
  migration/full-suite validation. The agent intentionally did not duplicate that full suite.
