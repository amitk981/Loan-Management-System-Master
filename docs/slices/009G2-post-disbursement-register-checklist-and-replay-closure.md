# Slice 009G2: Post-Disbursement Register, Checklist, and Replay Closure

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Complete the source-required post-transfer facts: one durable Loan Register update, one pending
borrower-advice identity, a reachable Senior Finance checklist sign-off, and exact §45.2 replay.

## Depends On
- 009E4
- 009G

## Runtime Capabilities

postgresql-five-race-acceptance

## Source / Review References
- `docs/source/functional-spec.md` BR-053-BR-054 and M08-FR-007-M08-FR-011
- `docs/source/integrations.md` §§9.1-9.10, 19.3, and 21
- `docs/source/api-contracts.md` §§27.7, 31.4-31.5, and 45
- `docs/source/data-model.md` §§18.1, 18.4, 19.3-19.4, and 34
- `docs/source/auth-permissions.md` §§15.6, 16.3, 18, 26.5, and 30
- `docs/source/codebase-design.md` §§16.4, 22, 26, 36-37, and 42
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-17_164724_architecture_review`

## Concrete Requirements
1. Extend the one public `DisbursementWorkflow.mark_transfer_successful` transaction so successful
   transfer/account activation also creates one protected pending borrower-advice communication or
   outbox identity and one durable Loan Register update identity. Bind both to the exact transfer,
   account, application/member, amount, normalized-reference digest, evidence checksum, and action/
   audit/workflow facts. `loan_register_updated_flag` may be true only with the singular coherent
   register evidence; never set a truth-only boolean or claim advice was sent.
2. Return the stable pending advice communication identity in §31.4. Exact key/payload/actor replay
   must use §45.2's `idempotency_replayed: true` plus the retained original response, with no new
   transfer, balance, status, register, communication, audit, workflow, or task writes. Changed key/
   payload or changed retained evidence remains a zero-write conflict.
3. Make the existing §27.7 Senior Manager Finance checklist-signature route consume the exact
   successful-disbursement decision through a top-level coordinator/narrow immutable selector; do
   not introduce `legal_documents -> disbursements` or another source-forbidden dependency. The
   signer must be active, carry `documents.checklist.sign_disbursement_complete`, have the source
   Stage-5 loan/application scope, and be distinct from any role not authorised by §16.3.
4. The first valid post-transfer signature creates one immutable checklist action/audit/workflow
   bound to the exact current transfer/register/advice-intent identities. Exact replay is zero-write;
   changed actor/comment, stale transfer/evidence, duplicate chain, missing register/advice intent,
   or pre-success call conflicts without altering financial or documentation truth.
5. Keep repayment/schedule/interest/default/closure behavior absent. Do not send the advice here;
   009H2 owns provider delivery of the stable pending identity.

## Test Cases
- Public transfer success proves atomic transfer, funded activation, Loan Register evidence, pending
  advice identity, safe ledgers, exact §31.4 response, and no sent/checklist/repayment side effects.
- Exact §45.2 replay asserts the nested original response and unchanged counts; changed replay,
  duplicate reference, and each altered register/advice/evidence relation fail closed.
- Public §27.7 calls cover correct Senior Finance signer, governed multi-role authority, inactive/
  permission-only/role-only/cross-object/pre-success denial, exact replay, and changed replay.
- Twice run five-caller PostgreSQL transfer and checklist races, retaining one complete transfer/
  register/advice-intent winner and one complete checklist-signature winner with clean losers.

## Evidence Required
Failing-first FR-009/011 and §45.2 probes; atomic post-transfer manifest; public checklist matrix;
sanitized responses; twice-run PostgreSQL races; focused tests, check/migration sync, and full gates.

## Risk Level
High

## Acceptance Criteria
- M08-FR-009 and M08-FR-011 have reachable, current-evidence-backed public paths.
- Transfer success cannot persist without exact register and pending-advice truth, and replay follows
  the source §45.2 contract without duplicate writes.
- Advice remains honestly pending until 009H2 accepts delivery; no later financial truth is invented.

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
- [ ] Commit delegated to the orchestrator after gates
