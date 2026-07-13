# Slice 007H3: Frozen Case Provenance and Read-Scope Parity Closure

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007H2

## Runtime Capabilities

none

## Goal

Make the enriched approval case's frozen provenance—not later mutable appraisal rows—the sole
coherence source for case detail, actions, sanction decisions, and register row scope.

## Source / Review References

- `docs/source/api-contracts.md` §§8 and 25.3-25.9
- `docs/source/data-model.md` §§15.3-15.6 and §34
- `docs/source/codebase-design.md` §§13.1, 26.1-26.3, 27.1, and 42.1-42.2
- `docs/slices/007F2-exception-routing-coherence-and-explicit-projection-closure.md` requirement 4
- `docs/slices/007H2-sanction-decision-and-register-object-scope-closure.md` requirements 1, 2,
  and 5
- `docs/working/REVIEW_FINDINGS.md` entry for
  `2026-07-13_222951_architecture_review`

## Concrete Requirements

1. At enrichment, validate the locked appraisal and loan-limit source through its owning credit
   interface, then freeze every provenance fact required for later coherence on the approval case.
   Once frozen, `is_routable_approval_case` must not compare those facts with the mutable live
   `LoanAppraisalNote.loan_limit_snapshot_json` or any later appraisal revision.
2. Saving a live appraisal directly or correcting/re-reviewing it through the public returned-cycle
   workflow must not change an earlier cycle's detail status, queue/history attribution, available
   actions, sanction-decision scope, or register visibility. Historical reads continue to serialize
   the original case `loan_limit_provenance_json` and `appraisal_facts_json` byte-for-byte.
3. Use one approval-owned frozen-case validity and actor-scope decision for collection/detail,
   sanction decision, and Credit Sanction Register. Apply it before register filters, counts, page
   normalization, and serialization. A row cannot be visible through §25.8/§25.9 when the same
   actor's canonical case detail is hidden as incoherent, nor can detail disappear while the
   immutable decision/register remains in scope because a live appraisal changed.
4. Do not promote `routing_snapshot_is_coherent`, a stale required-approver index, endpoint
   permission, Exception Register presence, or meeting metadata into authority. A direct malformed
   case-snapshot save must fail closed consistently across detail/action/decision/register with
   nondisclosing counts and zero writes; a live-owner change outside the frozen snapshot must leave
   all four boundaries unchanged.
5. Keep the projection seam explicit. Do not restore model-save signals or cross-table `save()` side
   effects. If a database-narrowing projection is retained, full frozen validation and count parity
   must remain testable through the public approval boundary.
6. Split the long exception/object-scope acceptance into focused public tests where practical while
   retaining one end-to-end tracer. Update `API_CONTRACTS.md` and the Epic 007 digest with the final
   frozen-versus-live ownership rule.

## Test Cases

- RED/GREEN public probe: GET an enriched pending case, mutate only the live appraisal policy name,
  then GET/list/act again; every frozen response and action decision is unchanged and the stored
  projection/index performs no hidden write.
- Return -> public correction -> fresh review -> new cycle: the returned cycle remains readable
  with its original provenance while the new pending cycle carries its new facts; actors/counts do
  not cross between cycles.
- Terminal parity: after approval, change the live appraisal and assert case detail, sanction
  decision, and the actor-scoped one-row register all remain readable and mutually attributable.
- Malformed frozen snapshot with a stale true projection/index: detail/action/decision/register all
  fail closed for that case before counts/pagination, without leaking or mutating any ledger.
- Original/effective/conflicted/acted and persisted legal/audit/management readers retain their
  007H2 scope only for frozen-valid cycles; endpoint permissions remain independent.

## Risk Level
High

## Acceptance Criteria

- Later appraisal changes cannot hide or rewrite a frozen approval cycle.
- Detail, action, sanction-decision, and register scope agree before counts and pagination.
- No hidden model-save projection returns, and all configured gates pass with retained RED/GREEN
  public evidence.
