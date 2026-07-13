# Slice 007D3: Returned Approval Cycle and Resubmission Closure

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007D2

## Runtime Capabilities

none

## Goal

Turn return-for-clarification into a usable immutable cycle: preserve the returned decision, allow
the corrected/re-reviewed appraisal to be submitted again, and route a new approval case without
rewriting the prior case or action ledger.

## Source / Review References

- `docs/source/data-model.md` approval cardinality (`loan_applications ||--o{ approval_cases`) and
  §§15.3-15.5/§34
- `docs/source/codebase-design.md` §13.1 invariant: re-approval after material change creates a new
  cycle
- `docs/source/api-contracts.md` §§24.4-25.8
- `docs/source/functional-spec.md` M05-FR-007/008
- `docs/slices/006E3-appraisal-history-and-review-authority-hardening.md`
- `docs/slices/007D-approval-action-api-approve-reject-return.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_131622_architecture_review`

## Concrete Requirements

1. Replace the one-case-per-application/appraisal restriction with immutable numbered approval
   cycles. Persist a positive `cycle_number`; enforce unique application + cycle and at most one
   open/pending cycle. Existing cases migrate deterministically to cycle 1. Approval actions and
   sanction decisions remain linked to the exact historical case.
2. Return closes only the current cycle and preserves its required/excluded approver snapshots,
   actions, version, audit, workflow, and notification evidence. It must expose a source-state
   transition that lets the appraisal maker supply clarification/material corrections and requires
   a fresh independent Credit Manager review before another sanction submission; never relabel the
   old review as approval of changed facts.
3. A subsequent submit creates cycle N+1 through the existing sanction-handoff boundary only when
   the prior cycle is returned and the latest immutable review matches the corrected appraisal.
   Pending, approved, or rejected prior cycles reject resubmission; concurrent resubmissions create
   one new shell and one evidence set.
4. Enrichment resolves and freezes the new cycle's current appraisal/configuration facts without
   mutating any earlier case. List/detail/action APIs expose `cycle_number` and allow an authorised
   reader to distinguish current work from immutable returned history.
5. Final approval creates the application-unique sanction decision from the latest cycle only.
   Earlier returned actions can neither satisfy the new cycle nor appear as its approver decisions.

## Test Cases

- Real submit -> enrich -> return -> maker correction -> fresh review -> resubmit -> enrich ->
  partial/final approval path with cycle 1 byte-for-byte unchanged.
- Resubmit without correction/fresh review and from pending/approved/rejected cycles is denied with
  complete no-write ledgers.
- Concurrent resubmission creates one cycle-2 case/evidence set; prior-cycle action uniqueness does
  not block the same approvers from acting in cycle 2.
- Current queue versus returned-history list/detail projections are unambiguous and object-scoped.

## Evidence Required

Failing dead-end resubmission test before the correction, green full two-cycle workflow, concurrent
resubmission proof, migration fixtures, immutable old-cycle ledgers, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- Return-for-clarification no longer leaves the application permanently unable to re-enter sanction.
- Every material re-approval is a new immutable case/review cycle; prior decisions never leak forward.

