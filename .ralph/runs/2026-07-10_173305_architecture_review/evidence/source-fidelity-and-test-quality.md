# Source Fidelity, Test Quality, And Functional IDs

## Substantive test evidence

- 005I5 asserts neutral owner state through staff- and portal-created applications, shared
  adult/minor/missing-evidence outcomes, invalid staff/portal mutation preservation, safe portal
  rendering, and production controller browser paths. Browser execution remains the existing A-013
  optional-gate limitation; the specs compile/list and mandatory frontend gates pass.
- 006D2B directly asserts both formula branches, below/equal/above boundaries, Decimal-equivalent
  acreage, null profile, invalid source evidence, failed-rerun preservation, canonical public/audit
  equality, resolver direction, requested locks, and rollback. Its missing real concurrency outcome
  proof is isolated in 006D2C.
- 006D3 creates pre-move rows, migrates forward/reverse, and proves the same UUIDs, FKs, table
  names, audit entity ID, and workflow entity ID. SQL evidence is empty.
- 006E asserts create/read/PATCH/submit behavior, strict/unknown/nested validation,
  permission/object denial, prerequisite gates, exact TAT boundary, no repeated transition, audit
  redaction, and create rollback. Missing immutable content, repayment capacity, retained submit
  reason, and update/submit failure rollback are owned by 006E2.

## Functional requirement disposition

Neither Epic 005 nor Epic 006 is marked Complete.

- M03-FR-003/M03-FR-009: selected nominee capture and mandatory same-member/adult evidence are
  reachable and reviewed in 005I5.
- M04-FR-001/002: explicitly deferred to 012EA by A-053; 012EA now contains exact appraisal task
  generation, Deputy Manager role assignment, close/reopen, idempotency, and backfill tests.
- M04-FR-003: implemented with `application.created_at` as receipt proxy; A-054 records the
  completeness-confirmation ambiguity.
- M04-FR-004-007: implemented by eligibility and loan-limit slices; 006D2B preserves their module
  behavior and 006D3 changes only ownership state.
- M04-FR-008: recommendation amount, tenure, interest/rate basis, and security are implemented.
- M04-FR-009: risk assessment is implemented; repayment-capacity notes remain partial until 006E2.
- M04-FR-010: Credit Manager review and sanction gate remain queued in 006F/006G.
- M04-FR-011: terminal Credit Manager rejection plus Rejection Note is now explicitly queued in
  006F2; a returned-for-revision decision is not counted as rejection.
