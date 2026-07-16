# Slice 009B2: SAP Delivery, Replay, Audit, and Owner-Seam Closure

## Status
Complete

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement

## Depends On
- 009B

## Runtime Capabilities

- `postgresql-five-race-acceptance`

## Goal

Make the manual SAP boundary genuinely deliver the exact retained Annexure-I, freeze exact completion
input, emit source-required audit truth, and establish the source-defined SAP workflow/adapter owner
before loan-account creation consumes its code.

## Source / Review References

- `docs/source/codebase-design.md` §§16.1, 20.3-20.4, 22, and 36.2
- `docs/source/integrations.md` §§8.1-8.5 and INT-SAP-001 through INT-SAP-006
- `docs/source/api-contracts.md` §§6-8 and 29
- `docs/source/auth-permissions.md` §§30.1-30.3 and 34.7
- `docs/source/functional-spec.md` BR-047 through BR-050 and M07-FR-001 through M07-FR-008
- `docs/slices/009A-sap-customer-code-request.md`
- `docs/slices/009B-sap-customer-code-confirmation-and-reuse.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-16_072819_architecture_review`

## Concrete Requirements

1. Establish `sap_workflow.modules.sap_customer_profile` as the real public policy owner and one
   manual `SapAdapter` implementation matching codebase-design §20.4. Preserve applied table/data
   history through a state-only migration/compatibility seam if required; do not duplicate SAP rows
   or let future loan/disbursement modules import private `finance` implementations.
2. The draft→sent transition succeeds only after the manual adapter accepts the exact checksum-
   verified/decrypted retained Annexure-I for the frozen active assignee. Persist an immutable file
   attachment/delivery reference or assignee-bound short-lived content capability—not a UUID in
   message text—and provide an audited, nondisclosing download/read path for that exact assignee.
3. Delivery remains manual/file-first and does not call real email/SAP services. Exact send replay
   returns the retained delivery identity; changed remarks/file/checksum/assignee or stale capability
   conflicts with no new communication/task/audit/workflow/file artifacts.
4. Freeze the normalized complete-request input (customer/vendor code, SAP timestamp, confirmation
   document, and notes) or its canonical digest on the completed request. Replay is 200 only when
   every supplied/omitted field exactly matches the first accepted payload; adding or omitting a
   retained optional value later is a changed replay and returns 409.
5. Emit mandatory `sap.customer_code_created` audit vocabulary on new code confirmation and one
   explicit reuse event without duplicating success facts. Every create/send/complete/read-sensitive
   audit includes actor user/type, role and team at action time, entity, old/new state, request id,
   IP/user-agent, timestamp, and safe reason/outcome; no identity/bank/workbook plaintext leaks.
6. Keep global normalized code uniqueness, one active member code, frozen current-sanction scope,
   assignee ownership, evidence provenance, zero loser writes, and no account/readiness/payment/
   disbursement side effects. Update API contracts and Epic 009 traceability for M07-FR-001-008.

## 008M4 Boundary Sharpening

- Follow the completed 008M4 deep-owner pattern: callers receive an SAP-owned decision/capability
  and do not query SAP tables, reconstruct adapter requests, or translate adapter exception classes.
- Keep queue/read projections bounded before any workbook decryption or delivery-capability issue;
  no list response may open the retained Annexure-I.

## Test Cases

- Both architecture-review SAP probes close: the assignee receives/reads the exact workbook through
  the adapter boundary, and changed optional reuse payload returns 409 with unchanged ledgers.
- Public send/download tests cover attachment checksum, ciphertext-at-rest, one-use/expiry/tamper,
  replacement, cross-user/application/request/file denial, and exact one download audit.
- Audit matrices assert exact mandatory vocabulary plus role/team/request/network snapshots and
  recursive secret absence for create, send, new confirmation, reuse, replay, and denial.
- Dependency guards prove downstream callers use the SAP owner interface and manual/fake adapters
  satisfy the same contract. Twice-run PostgreSQL request/code races retain exact winner and zero
  loser artifacts after the owner transfer.

## Evidence Required

Failing-first copies of both review probes; adapter contract output; sanitized send/download/
complete/reuse/audit examples; migration/ownership proof; focused API/service tests; twice-run
PostgreSQL races; full configured gates.

## Risk Level
High

## Acceptance Criteria

- `sent` means the frozen assignee can receive the exact retained Annexure-I through the governed
  manual adapter boundary.
- Completion replay is byte-for-byte/canonical-field exact and SAP audit events meet source rules.
- One source-defined SAP owner protects all existing uniqueness, scope, concurrency, and secrecy
  guarantees, with no downstream financial side effects.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated
- [x] Database rules followed
- [x] Permissions tested
- [x] Audit events tested
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [x] Commit delegated to the orchestrator only after passing configured gates
