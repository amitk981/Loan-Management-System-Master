# Slice 007K: Frozen Review Snapshot and Selector Boundary Closure

## Status
Complete

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007H3

## Runtime Capabilities

none

## Goal

Make the approval case's persisted review snapshot mandatory immutable truth and restore one-way
dependency flow between the approval engine and its query selector.

## Source / Review References

- `docs/source/codebase-design.md` §§7.2, 13.1, 26.1-26.3, 27.1, and 36.1
- `docs/source/api-contracts.md` §§25.3-25.10 and §44
- `docs/source/data-model.md` §§15.3-15.6 and §34
- `docs/source/functional-spec.md` M05-FR-002/007/009
- `docs/slices/007H3-frozen-case-provenance-and-read-scope-parity-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_010536_architecture_review`

## Concrete Requirements

1. A routable cycle must carry a non-empty, schema-complete `appraisal_facts_json` frozen by the
   credit-owned enrichment interface. Case detail must serialize that object byte-for-byte; it
   must never call the live appraisal to synthesize missing review facts.
2. Remove the live `loan_appraisal_note.reviewed_at` / `recommended_amount` fallback from canonical
   validity. An empty, partial, malformed, or case-inconsistent frozen review snapshot must fail
   closed across collection, detail, actions, sanction decision, Exception Register, and Credit
   Sanction Register even when stored coherence/read indexes remain true.
3. Restore dependency direction `approval engine -> selector/models`. The selector may shape and
   prefetch actor-scoped candidate queries but must not import the approval engine or execute its
   business-validity policy. Expose one approval-owned public read boundary that all case,
   decision, and register callers use before filters, counts, pagination, or serialization.
4. Do not restore signals, model-save side effects, or trust a Boolean/index as authority. Keep
   direct malformed-save regressions and explicit-writer projection refreshes.
5. Replace exact ORM-query-count/literal-SQL assertions with observable boundary assertions. A
   focused performance assertion may bound candidate/page work without pinning Django's SQL text.
6. Inspect migrated/seeded rows. If any legitimate retained cycle lacks frozen review facts, use
   existing immutable history/evidence to backfill it in the single allowed migration; never copy
   later mutable appraisal truth into an older cycle. If historical truth is unavailable, leave
   the row nondisclosing and record the remediation fact rather than inventing it.

## Test Cases

- RED/GREEN: clear `appraisal_facts_json` while leaving stored coherence/read rows true; every
  public read/action/register boundary fails closed with zero ledger writes and zero leaked count.
- Mutate only the live appraisal after a valid pending and terminal case exists; the complete
  frozen detail/history/decision/register responses remain byte-for-byte unchanged.
- Return, correct, re-review, and create cycle 2; cycle 1 and cycle 2 retain distinct mandatory
  review snapshots with no live fallback.
- Static dependency regression proves the selector does not import the approval engine and all
  decision/register callers cross the single public approval read boundary.

## Risk Level
High

## Acceptance Criteria

- Missing frozen review truth cannot be repaired or authorised from mutable live appraisal rows.
- Approval read dependency flow is acyclic and all pre-pagination consumers share one deep seam.
- Backend RED/GREEN evidence and all configured gates pass.
