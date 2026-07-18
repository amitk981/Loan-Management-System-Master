# Slice 009H6: Legacy Advice Template Provenance Closure

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Stop pre-009H4 advice rows from presenting template facts reconstructed from a later mutable
template row as verified historical provenance.

## Depends On
- 009H4

## Source / Review References
- `docs/source/functional-spec.md` BR-054 and M08-FR-010
- `docs/source/codebase-design.md` §§20.6, 26.3, 36.1-36.2, and 42.4
- `docs/source/integrations.md` §§10, 19.3, 21, and 33.3
- `docs/source/data-model.md` §34
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-18_152831_architecture_review`
- Review probe `evidence/review-probes/review_contract_probes.py`

## Concrete Requirements
1. Add one communications migration that identifies every provenance row/attempt created by the
   0005 legacy backfill. Facts copied from the then-current template FK must be labelled
   `legacy_partial`, never `verified`; do not guess the original name/type/language/audience/
   approval/effective range/variables/source templates or checksum.
2. Preserve coherent historical provider/receipt/Communication/action/audit/workflow truth and keep
   it permanently nondispatching. Legacy-partial provenance may remain reviewable as retained
   history but cannot become current portal/download/replay truth until a separately governed
   successor is created; no existing evidence is rewritten as a new delivery.
3. New post-0005 outboxes remain `verified` only when all provenance was frozen before dispatch.
   Reconcile provenance status, accepted-attempt identity/digest, terminal links, and template
   snapshots together so a status flip or copied current template cannot upgrade history.
4. Forward/reverse/reapply must preserve ids, tables, provider facts, receipts, Communications,
   actions, audits, workflows, and ambiguity. Reverse is allowed only at a truthful safe boundary.

## Test Cases
- Copy the failing review probe first and add a genuine migration fixture whose template changes
  between retained delivery and migration; migration must not bless the later values.
- Cover retained outbox, pre-outbox delivery, accepted-not-finalized, pending, malformed/ambiguous,
  and post-0005 verified rows through forward/reverse/reapply.
- Public replay/download makes zero provider calls and refuses legacy-partial provenance without
  deleting or replacing historical evidence.

## Runtime Capabilities

postgresql-five-race-acceptance

## Database / Migration Impact
Exactly one communications migration; no destructive history rewrite.

## Risk Level
High

## Acceptance Criteria
- No later mutable template row can become claimed historical provenance.
- Coherent legacy delivery remains preserved and nondispatching while only genuinely frozen new
  provenance can satisfy current advice truth.

## Done Checklist
- [ ] Execution plan written
- [ ] Legacy template-drift migration probe written failing first
- [ ] Honest provenance migration/current selector implemented
- [ ] Migration manifests and public no-redispatch tests green
- [ ] PostgreSQL acceptance green twice
- [ ] Risk, evidence, handoff, state, and digest updated
- [ ] Commit delegated to the orchestrator after gates

