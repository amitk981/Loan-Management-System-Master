# Slice 009B3C: SAP Current-Evidence and Adapter-Contract Closure

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement

## Depends On
- 009B3B

## Runtime Capabilities

none

## Goal

Make the public SAP decision depend on the complete singular retained delivery/completion evidence
and prove that Manual, Fake, and Future adapters enforce the same negative as well as happy paths.

## Source / Review References

- `docs/source/codebase-design.md` §§16.1, 20.3-20.4, 26-28, 36.2, and 42
- `docs/source/integrations.md` §§8.1-8.5 and INT-SAP-001 through INT-SAP-006
- `docs/source/api-contracts.md` §§6-8 and 29
- `docs/source/auth-permissions.md` §§30.1-30.3 and 34.7
- `docs/source/data-model.md` §§19.1-19.2, 28-30, and 34
- `docs/source/functional-spec.md` M07-FR-001 through M07-FR-008 and M07-FR-010
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-16_213746_architecture_review`

## Concrete Requirements

1. Reconcile one exact send action/audit/workflow/task/communication/delivery tuple and one exact
   completion action/audit/workflow tuple before returning `SapCustomerCodeDecision`. Validate every
   retained safe field, actor/assignee, role/team, request/application/member/code, state transition,
   workbook/file/checksum, supplied/omitted digest, reuse flag, and linked identity.
2. Extra, missing, duplicate, changed, unrelated, reordered, or cross-request send/completion
   evidence invalidates the public decision without exposing customer code, workbook, capability,
   or internal ledger ids. Mutable request/code labels alone never restore it.
3. Keep the evidence decision entirely in the canonical `sap_workflow` owner. Downstream loans and
   disbursements consume only the immutable decision; no Finance model/policy/storage import or
   parallel selector returns.
4. Run one shared adapter contract against Manual, Fake, and Future. It must cover exact idempotent
   replay and reject checksum mismatch, non-XLSX bytes, changed file/assignee/key, malformed delivery
   reference, and a Future transport that attempts to bypass local workbook validation.
5. Preserve the 009B2 routes, response shapes, error taxonomy, encryption/redaction, one-use delivery
   capability, model/table identity, audit vocabulary, and manual/file-first behavior. No schema or
   real SAP/email transport is introduced.

## Test Cases

- Reproduce the review probe by changing the send audit assignee while retaining its checksum; the
  current decision becomes absent. Repeat for every safe send/completion body field and every
  singular linked ledger, including duplicate sibling rows and changed workflow/task relations.
- Prove exact genuine create/send/download/complete/reuse/read flows still return the current
  decision and that denials leave SAP, loan, checklist, audit, workflow, task, and communication
  truth unchanged.
- Parameterize Manual/Fake/Future positive, replay, invalid checksum, invalid bytes, changed
  idempotency facts, bad reference, and rejecting transport cases through the same contract.
- For every adapter denial, assert zero new request/code/delivery/communication/task/audit/workflow
  rows; exact replay must return the original delivery reference and changed assignee, capability,
  workbook checksum, or idempotency key must conflict without invoking the transport twice.
- Dependency/import tests prove canonical model identity and no executable SAP-to-Finance edge.

## Evidence Required

Failing-first SAP evidence probe; sanitized singular-ledger manifest; shared adapter contract;
public flow and denial results; dependency graph; focused tests and full configured gates.

## Risk Level
High

## Acceptance Criteria

- A SAP code is current only while its complete owner-held delivery and completion evidence agrees.
- Manual, Fake, and Future adapters enforce one substitutable positive and negative contract.
- Existing API, state, secrecy, replay, and model-ownership guarantees remain exact.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit delegated to the orchestrator only after passing configured gates
