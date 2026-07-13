# Slice 007F2: Exception Routing Coherence and Explicit Projection Closure

## Status
Complete

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007H

## Runtime Capabilities

none

## Goal

Make a real exception application travel from reviewed appraisal through enrichment, scoped reads,
all required decisions, and both generated registers without becoming hidden by a contradictory
coherence projection; remove the remaining hidden model-save projection mutation.

## Source / Review References

- `docs/source/functional-spec.md` M05-FR-003, M05-FR-006, and M05-FR-009
- `docs/source/api-contracts.md` §§25.2-25.10 and §44
- `docs/source/data-model.md` §§15.2-15.7 and §34
- `docs/source/codebase-design.md` §§13.1, 26.1-26.3, 27.1, and 42.1-42.2
- `docs/slices/007E2-conflict-authority-projection-and-scope-closure.md` requirement 6
- `docs/slices/007F-exception-approval-workflow.md` requirements 1-3
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_200023_architecture_review`

## Concrete Requirements

1. Derive the non-forced exception predicate from coherent frozen facts: the reviewed recommended
   amount must exceed the frozen `final_eligible_loan_amount`, and the stored loan-limit exception
   flag must agree. A contradictory amount/flag snapshot returns a stable invalid-state response and
   creates no routing, register, audit, workflow, or communication writes. A caller-supplied
   `force_exception_route: true` remains the only explicit within-limit route and requires its
   truthful bounded exception type and business reason.
2. Reconcile the case coherence invariant with 007F's distinct `reason_for_approval` and Exception
   Register `business_reason`. Do not require those independently authored facts to be equal. The
   routed case must instead prove that its exception condition, case exception reason, same-case
   register type/reason/risk, frozen loan-limit provenance, and matrix condition describe one
   internally consistent exception decision.
3. A successful public exception enrichment must persist
   `routing_snapshot_is_coherent=true`, appear in ordinary and assigned list counts, return from
   detail, accept the exact CFO + two-Director action sequence, close the same-case Exception
   Register row, and create the terminal Credit Sanction Register row. No test may manually attach
   the Exception Register entry or mutate routing facts between those public calls.
4. Remove the appraisal `post_save` projection side effect. Approval coherence and reader-index
   synchronization remain behind the single approval-owned projection interface and are invoked
   explicitly by every approval-owned case writer. Saving either an `ApprovalCase` or a
   `LoanAppraisalNote` directly must not mutate another table or silently change read authority.
   Historical closed cycles continue to read their frozen facts rather than following live
   appraisal mutations.
5. Replace private-helper acceptance with public module/HTTP interface tests. Retain small pure
   validation tests only where no public behavior can discriminate the rule. Document the corrected
   invariant and distinct reason ownership in `API_CONTRACTS.md` and the Epic 007 digest.

## Test Cases

- RED/GREEN tracer: reviewed above-limit application -> submit -> enrich with distinct approval and
  business reasons -> list/detail -> CFO + two Directors approve -> Exception Register approved ->
  Credit Sanction Register/sanction decision readable; assert exact ids, counts, facts, and evidence.
- Contradictory frozen matrices: below/equal amount with flag true and above amount with flag false;
  both are stable zero-write denials. Forced within-limit waiver remains a coherent public route.
- Exact enrichment replay is zero-write; changed business reason, risk, type, amount, or frozen
  provenance conflicts without hiding or rewriting the original case.
- Direct appraisal and case saves do not mutate coherence/read-index rows; each production approval
  writer refreshes exactly once inside its owner transaction, including return/new-cycle history.

## Risk Level
High

## Acceptance Criteria

- A source-valid exception case is actionable through the complete public workflow and cannot be
  hidden by a reason-field mismatch.
- No ordinary Django model save hides approval projection or object-scope mutation.
- All configured gates pass with retained RED/GREEN evidence.
