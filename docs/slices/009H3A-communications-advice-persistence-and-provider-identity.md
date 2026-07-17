# Slice 009H3A: Communications Advice Persistence and Provider Identity

## Status
Complete

## Origin
Oversized slice: `009H3`

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Depends On
- 009H2

## Goal
Make communications the canonical owner of the retained advice receipt and durable pre-dispatch
outbox state, and establish payload-independent Manual/Fake/Future provider identity, without yet
moving the complete public advice orchestration out of disbursements.

## Source / Review References
- `docs/source/functional-spec.md` BR-054 and M08-FR-010
- `docs/source/api-contracts.md` §§31.5, 39, and 45
- `docs/source/integrations.md` §§9-10, 19.3, and 21
- `docs/source/codebase-design.md` §§20.6, 22.2, 26.3, 36.2, 40.1-40.2, and 42.4
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-17_210855_architecture_review`
- Retained oversized run `.ralph/runs/2026-07-18_010406_normal_run/`

## Concrete Requirements
1. Define `CommunicationDeliveryOutbox` in communications as the canonical protected persistence
   owner for one advice intent/communication identity, stable idempotency key, channel, frozen
   recipient and recipient digest, approved template/version/checksum provenance, rendered
   subject/body and canonical payload digest, related entity type/id, status, and provider result.
   Enforce one outbox per advice intent, communication identity, and idempotency key.
2. Move Django model-state ownership of `DisbursementAdviceDeliveryReceipt` from disbursements to
   communications while retaining the physical table `disbursement_advice_delivery_receipts`,
   primary keys, advice-intent relation, provider id/status/time, complete-row constraint, unique
   relations, and every historical row. Do not rename, drop, recreate, copy, or rewrite the table.
3. Implement this slice's complete database change in one communications-owned migration: create
   the outbox table and perform the receipt owner transfer through reversible state-only operations.
   Fresh install, forward, reverse, and reapply must produce the same model/schema state without a
   disbursements-to-communications migration cycle.
4. Keep Manual, Fake, and Future email-adapter contracts in communications. Provider identity must
   derive from the stable idempotency key rather than mutable payload: repeated calls under one key
   expose one logical external identity/status, including across fresh adapter instances. Provider
   rejection remains retryable and does not fabricate an accepted receipt or sent communication.
   No real network delivery is introduced.
5. Preserve a one-way, policy-free compatibility seam for existing 009H2 callers until 009H3B moves
   template/render/dispatch/finalization policy. Compatibility imports must resolve to the canonical
   communications models/adapters and contain no duplicate manager, query, rendering, delivery,
   receipt, or audit implementation.
6. Preserve the exact 009H2 public route, response/errors, role/object scope, current-contact and
   upstream reconciliation, recipient masking, safe audit behavior, and no-financial-side-effect
   rules. This foundation must be independently green and must not claim the terminal crash-window
   closure owned by 009H3B.

## Test Cases
- A failing-first ownership test proves the canonical outbox and receipt model metadata belongs to
  communications while the receipt's physical table, constraints, relation, and retained id do not
  change.
- Migration-executor tests create a genuine delivered receipt in the exact pre-009H3A state,
  capture its table/constraint signature and ids, migrate forward, reverse, and reapply, and assert
  identical receipt rows plus exactly one valid outbox schema and no duplicate state.
- One shared Manual/Fake/Future adapter contract proves stable-key provider identity independently
  of payload mutation, exact replay across fresh adapters, rejection/retry, and replaceability. It
  must distinguish provider identity from 009H3B's frozen-outbox payload-conflict policy.
- Import/compatibility tests reject a communications-to-disbursements model/policy cycle and prove
  legacy names are aliases or shallow forwarders with no second persistence or adapter policy.
- Retained public 009H2 success/replay/rejection/permission tests remain green with unchanged HTTP,
  audit, workflow, Communication, receipt, and financial facts.

## Evidence Required
Failing-first ownership and adapter-contract output; before/after receipt schema and row-identity
manifest; forward/reverse/reapply migration plan and migration-sync output; Manual/Fake/Future
contract results; compatibility/import graph; focused 009H2 regressions; Django check; protected-
path and diff-limit results. Recreate the retained run's migration-state evidence in this slice's
own run folder rather than treating failed-candidate evidence as acceptance.

## Retained Failed-Run Evidence Allocation
- `evidence/migration-state-manifest.md` and the owner-transfer portion of
  `green-adapter-migration-attempt-1.txt` define this slice's preservation proof.
- Adapter identity portions of the retained focused logs define the shared contract baseline.
- The crash/template-drift, final-dispatch, and PostgreSQL race logs remain allocated to 009H3B.

## Runtime Capabilities

none

## Database / Migration Impact
Exactly one communications migration. It creates the durable outbox and transfers receipt model
state without any receipt-table database operation or retained business-data rewrite. 009H3B adds
no migration.

## Predicted Diff Budget
Target 700-1,050 changed lines across models, adapters, one migration, migration/adapter tests, and
evidence; stop and resplit before implementation if the forecast exceeds 1,500 lines. This remains
comfortably below the configured 2,000-line limit and leaves orchestration/race work to 009H3B.

## Risk Level
High

## Material Risks
- Historical receipt loss, duplicate schema state, or constraint drift during owner transfer.
- A communications-to-disbursements dependency cycle or a policy-bearing compatibility layer.
- Provider identity accidentally depending on changed content rather than the stable key.
- Premature sent/receipt truth after provider rejection or drift in the existing public contract.

## Acceptance Criteria
- Communications canonically owns the outbox and retained receipt state with identical historical
  receipt storage and one non-destructive migration.
- Manual/Fake/Future adapters expose one key-owned logical provider identity and retryable rejection.
- Existing 009H2 behavior remains independently green, ready for terminal dispatcher closure.

## Done Checklist
- [x] Execution plan written
- [x] Failing ownership/migration/adapter tests written first
- [x] Communications models and adapter identity implemented
- [x] State-only receipt transfer and outbox migration proved forward/reverse
- [x] Existing 009H2 public behavior preserved
- [x] Risk assessment, handoff, state, and evidence updated
- [x] Commit delegated to the orchestrator after gates
