# Slice 009B3: SAP Policy Owner and Dependency Closure

## Status
Superseded

## Superseded By

- 009B3A
- 009B3B

The first implementation attempt measured 2,885 changed lines against the 2,000-line slice limit.
The requirements below are preserved across the dependency-ordered successors.

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement

## Depends On
- 009B2

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Make `sap_workflow` the actual deep owner of SAP request, delivery, completion, code, and retained
workbook policy while preserving every applied Finance row and public API identity.

## Source / Review References

- `docs/source/codebase-design.md` §§16.1, 20.1-20.4, 22, 26-28, 36.2, and 42
- `docs/source/integrations.md` §§8.1-8.5 and INT-SAP-001 through INT-SAP-006
- `docs/source/api-contracts.md` §§6-8 and 29
- `docs/source/auth-permissions.md` §§30.1-30.3 and 34.7
- `docs/source/data-model.md` §§19.1-19.2, 28-30, and 34
- `docs/source/functional-spec.md` BR-047 through BR-050 and M07-FR-001 through M07-FR-008
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-16_143718_architecture_review`

## Concrete Requirements

1. Move executable request/create/send/complete/reuse/read/delivery-capability policy, retained
   Annexure storage decisions, and the canonical SAP model state behind
   `sap_workflow.modules.sap_customer_profile`. No executable `sap_workflow` file may import
   `finance.models`, `finance.modules`, or private Finance storage/policy helpers.
2. Preserve existing tables, ids, constraints, ciphertext, delivery/completion digests, audit/
   workflow/task relations, and migration history through state-only ownership migration or an
   equally non-destructive seam. Prove before/after row counts, ids, checksums, hashes, foreign keys,
   and table names; never copy or re-encrypt retained business data merely to change ownership.
3. Remove the bidirectional Finance↔SAP dependency. HTTP route shells and downstream loans/
   disbursements consume only the SAP public owner; any temporary legacy import is one-way,
   policy-free, explicitly tested, and has no model/query/action implementation of its own.
4. Keep the Manual/Fake/Future `SapAdapter` contract inside the SAP owner. `sent` still requires
   exact workbook acceptance and assignee capability; completion/reuse remains supplied/omitted-
   exact; all source audit vocabulary, secrecy, concurrency, and zero-side-effect guarantees remain.
5. Align touched SAP HTTP conflicts/stale-state responses with the source §7 standard vocabulary
   while preserving stable actionable field details. Do not create a second parallel error taxonomy.

## Test Cases

- Dependency-graph tests parse imports for the entire `sap_workflow`, `finance`, `loans`, and
  `disbursements` packages and reject SAP→Finance executable edges or cycles; behavior tests cross
  only the public SAP interface, not source-text substring proxies.
- Migration tests load pre-009B3 state, apply forward/backward state transitions where supported,
  and assert exact table/row/id/FK/checksum/digest preservation with no duplicate SAP facts.
- Public create/send/download/complete/reuse/read tests retain exact 009B2 behavior, standard errors,
  safe mandatory audit context, ciphertext-at-rest, and no account/readiness/payment side effects.
- Twice-run PostgreSQL request/code races after ownership transfer retain exact one winner and zero
  loser success artifacts; Manual and Fake adapters pass the same contract suite.

## Evidence Required

Failing-first ownership/dependency probe; before/after model and migration graph; sanitized public
flows; adapter contract; focused tests; twice-run PostgreSQL races; full configured gates.

## Risk Level
High

## Acceptance Criteria

- `sap_workflow` owns SAP behavior and model policy without importing private Finance code.
- Existing data/API/audit/concurrency contracts survive the non-destructive owner transfer.
- Downstream Epic 009 code depends on one deep, replaceable SAP seam with no cycle.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Database rules followed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit delegated to the orchestrator only after passing configured gates
