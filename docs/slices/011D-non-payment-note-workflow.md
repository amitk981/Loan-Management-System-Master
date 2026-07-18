# Slice 011D: Non-Payment Note Workflow

## Status
Not Started

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance

## Goal
Prepare, freeze, and submit the formal Non-Payment Note only after an eligible one-year extension
expires unpaid.

## User Value
The recovery authority receives a complete, traceable case rather than an informal recommendation.

## Depends On
- 011C

## Source References
- `docs/source/api-contracts.md` §§35.6-35.7
- `docs/source/data-model.md` §21.4
- `docs/source/functional-spec.md` M12-FR-009-011
- `docs/source/screen-spec.md` S55
- `docs/source/security-privacy.md` §23.2
- `docs/source/test-plan.md` MOD-DEF-008, MOD-REC-001-003
- `docs/working/digests/epic-011-default-recovery-closure-compliance.md` §011D

## Scope
- Add one `NonPaymentNote` per case and recovery-domain operations to create a draft and submit it to
  the configured Sanction Committee/Board workflow.
- Permit creation only after the applicable extension expired unpaid. Derive outstanding principal
  and interest from canonical servicing/ledger truth; retain original due/grace/extension summary,
  current assessment, evidence, reason, recommendation, preparer, and status.
- Implement POST `/api/v1/default-cases/{id}/non-payment-note/` and POST
  `/api/v1/non-payment-notes/{id}/submit-to-sanction-committee/`.
- Submission freezes decision inputs, records submission time, and creates/reuses one approval task/
  case through the existing approval owner; post-submit edits require an explicit returned state.

## Permissions and Audit
- Credit Assessment creates with `defaults.non_payment_note.create`; Credit Manager submits with
  `defaults.non_payment_note.submit`; configured approvers and Auditor read only at this stage.
- Draft creation, submission, return, and denied/changed replay retain safe audit/workflow evidence.

## Acceptance and Negative Tests
- An unpaid expired extension yields one note with source-derived amounts and one submission task.
- Reject no extension, active extension, cured/closed/foreign case, missing narrative, negative or
  caller-mismatched amounts, foreign evidence, unauthorised submit, and mutation after submission.
- Exact replay and concurrent create/submit converge on one note and one approval chain.
- Reverse consumers: 011A-C timelines remain immutable; approval routing receives frozen note facts;
  no recovery action becomes available merely because a note exists.

## Non-Goals
Choosing recovery authority/action (011E), executing security (011F), write-off/settlement policy,
frontend, or changing the canonical ledger.

## Evidence
RED/GREEN gate/service/API/permission tests; migration/race proofs; frozen-snapshot and audit evidence;
reverse approval/default regressions; full backend gate and response examples.

## Risk Level
High

## Acceptance Criteria
- `DEFAULT-AC-005`, `REC-AC-002-003`, `MOD-REC-001-003`, and `API-REC-001-002` pass.
- Recovery approval cannot start from an absent, premature, mutable, or financially forged note.

## Done Checklist
- [ ] Execution plan and TDD evidence saved
- [ ] Persistence, service/API, approval handoff, permissions, and audit completed
- [ ] Negative, frozen-truth, race, reverse-consumer, and full gates passed
- [ ] Evidence saved; substantive risks/decisions recorded in review-packet/HANDOFF only when needed; mechanical bookkeeping left to Ralph
