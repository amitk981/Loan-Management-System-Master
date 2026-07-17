# Slice 009G3: Post-Transfer Aggregate and Checklist Integrity Closure

## Status
Complete

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Make Loan Register evidence structurally inseparable from successful-transfer truth and allow the
source-authorised current Senior Finance owner—not only the original initiator—to perform the exact
post-disbursement checklist sign-off with fully reconciled immutable evidence.

## Depends On
- 009E5
- 009G2

## Source / Review References
- `docs/source/functional-spec.md` M08-FR-009 and M08-FR-011
- `docs/source/auth-permissions.md` §§15.6, 16.3, 19.3, and 26.5
- `docs/source/data-model.md` §§19.3-19.4 and 34
- `docs/source/codebase-design.md` §§16.4, 21-22, 36-37, and 42
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-17_210855_architecture_review`

## Concrete Requirements
1. Replace truth-only `loan_register_updated_flag` semantics with a protected singular relation from
   the successful disbursement aggregate to its exact `LoanRegisterUpdate` (or an equally strong
   database-enforced owner link). Successful rows require it; pending/failed rows forbid it. The
   register cannot be deleted or reparented while success remains.
2. Keep transfer, funded activation, register, pending advice, action/audit/workflow, evidence file,
   and status history in the one public transaction. Current/replay selectors must reconcile the
   owner link and reject missing, duplicate, cross-object, or changed rows without presenting a true
   register flag.
3. Authorise checklist sign-off through the existing canonical Stage-5 loan scope: active persisted
   Senior Manager Finance with the explicit grant and current SAP/disbursement-linked application/
   loan scope. Do not require signer id to equal the historical initiating-maker id; role, permission,
   or an unrelated finance assignment alone remains insufficient.
4. Reconcile the complete singular checklist action/audit/workflow/version tuple on replay: meaning,
   comment, actor/role/team, request/network, old/new state, action ids, timestamps, relation ids and
   exact current transfer/register/advice facts. Changed/extra/missing sibling evidence conflicts.

## Test Cases
- Database attempts to delete/reparent the register or retain successful/true state without its
  protected owner relation fail atomically; pending/failed rows cannot carry it.
- Original initiator and a distinct current Stage-5 Senior Finance assignee succeed in valid scope;
  stale former assignee, permission-only, role-only, inactive, cross-loan, and CFC users are denied.
- Mutate every checklist action/audit/workflow/version relation/field independently and add duplicate
  siblings; exact replay fails with zero writes. Twice run transfer and checklist PostgreSQL races.

## Runtime Capabilities

postgresql-five-race-acceptance

## Database / Migration Impact
One disbursements-owned migration may add/replace the aggregate owner relation and constraints.
Preserve existing ids and backfill only rows with singular coherent 009G2 evidence; fail closed on
legacy ambiguity rather than fabricate register completion.

## Risk Level
High

## Acceptance Criteria
- M08-FR-009 truth cannot outlive its evidence, and M08-FR-011 remains reachable by the source-
  authorised current Senior Finance scope with exact immutable replay/race behavior.

## Done Checklist
- [x] Execution plan written
- [x] Failing tests written first and RED/GREEN evidence saved
- [x] Aggregate relation/constraint migration implemented
- [x] Public authority, ledger-tamper, and PostgreSQL tests passed
- [x] API contracts updated, if needed (no API shape changed)
- [x] Risk assessment, handoff, state, and evidence updated
- [x] Commit delegated to the orchestrator after gates
