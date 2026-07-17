# Slice 009H3: Communications-Owned Advice Outbox and Idempotency Closure

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Move template/render/delivery/receipt policy behind the source-defined communications owner and
close the provider-acceptance-before-receipt crash window with one durable advice outbox contract.

## Depends On
- 009H2

## Source / Review References
- `docs/source/functional-spec.md` BR-054 and M08-FR-010
- `docs/source/api-contracts.md` §§31.5, 39, and 45
- `docs/source/integrations.md` §§9-10, 19.3, and 21
- `docs/source/codebase-design.md` §§20.6, 22.2, 26.3, 36.2, 40.1-40.2, and 42.4
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-17_210855_architecture_review`

## Concrete Requirements
1. Make `communications.modules.communication_dispatcher` the single owner of approved/effective
   template resolution, variable/sensitive-value validation, rendering, protected Communication,
   durable outbox/provider receipt, adapter dispatch, delivery status, and communication audit.
   Disbursements supplies an immutable advice context and consumes an ordinary delivery decision.
2. Durably freeze the stable intent/idempotency key and canonical payload digest before the provider
   call. Same key plus changed recipient/template/subject/body/entity must conflict before dispatch
   even after a crash or fresh adapter; exact retry reuses one logical provider identity.
3. Manual, Fake, and Future adapter contracts treat idempotency identity independently of payload
   mutation. Repeated exact calls return one provider identity/status; changed payload under the same
   key is rejected by the frozen outbox. Provider rejection remains pending and retryable.
4. Transfer delivery-receipt model state/table ownership to communications without changing its
   physical table, ids, retained receipts, advice-intent relation, or historical delivery evidence.
   Keep disbursement intent/upstream facts in disbursements and avoid a dependency cycle.
5. Preserve 009H2 role/scope, current-contact/template/upstream reconciliation, recipient masking,
   safe response, and no-financial-side-effect rules.

## Test Cases
- Simulate acceptance followed by failure before receipt update and before final communication
  commit; a fresh adapter exact retry yields one provider identity, while changed payload/email/
  template conflicts with no second logical message.
- Five-caller PostgreSQL races record every adapter result and assert one external message identity,
  one frozen outbox, one receipt, one Communication, one action/audit/workflow, and clean losers.
- Manual/Fake/Future contracts cover exact replay, same-key changed payload, rejection/retry,
  malformed provider results, and no raw recipient/content in general audit.
- State-only owner-transfer migration proves identical table/constraints/ids forward and reverse.

## Runtime Capabilities

postgresql-five-race-acceptance

## Database / Migration Impact
One state-preserving owner-transfer/outbox migration. Do not rename/drop/recreate the retained
receipt table or duplicate receipt policy across applications.

## Risk Level
High

## Acceptance Criteria
- One stable advice key cannot produce two logical provider messages across any tested crash/race,
  and all communications policy is local to the source-defined owner behind a narrow interface.

## Done Checklist
- [ ] Execution plan written
- [ ] Failing crash/adapter/ownership tests written first
- [ ] Communications dispatcher/outbox owner implemented
- [ ] State migration and twice-run PostgreSQL evidence saved
- [ ] API contracts updated, if needed
- [ ] Risk assessment, handoff, state, and evidence updated
- [ ] Commit delegated to the orchestrator after gates
