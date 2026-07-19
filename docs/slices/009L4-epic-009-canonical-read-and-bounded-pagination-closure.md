# Slice 009L4: Epic 009 Canonical Read and Bounded Pagination Closure

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Close the remaining Epic 009 root boundary with one canonical SAP completion decision, owner-level
workspace action predicates, and truth-preserving pagination whose evidence work stays bounded as
the eligible portfolio grows.

## Depends On
- 009L3

## Runtime Capabilities

- `none`

## Source / Review References
- `docs/source/functional-spec.md` M07-FR-001 through M07-FR-010 and M08-FR-001 through M08-FR-011
- `docs/source/api-contracts.md` §§29-31 and 45
- `docs/source/auth-permissions.md` §§16.3, 19.2-19.3, 20.1, 25.7, 26.5, and 34.7
- `docs/source/codebase-design.md` §§16, 26, and 42
- `docs/working/API_CONTRACTS.md` Loan Account 360 and staff-workspace contracts
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-19_104332_architecture_review`
- `.ralph/runs/2026-07-19_104332_architecture_review/evidence/review-probes/test_009l3_contract_probes.py`

## Concrete Requirements
1. Give the SAP owner one public current-completion decision for a member and its exact
   application/customer-code edge. Member, account, readiness, staff workspace, Loan Account, and
   disbursement consumers must delegate to that decision instead of selecting their own request.
   A blank, changed, duplicate, newer-stale, cross-application, cross-member, inactive-code,
   audit/workflow, send/workbook, digest, actor, or assignment mismatch fails closed identically.
2. Move complex Loan Account eligibility into a canonical read selector that composes lifecycle,
   SAP, transfer, role/object scope, and relational coherence without copying partial owner rules
   into the process coordinator. Count and database pagination must operate on the exact eligible
   identity set; denied or incoherent rows affect neither totals nor page reachability.
3. Keep Loan Account and staff-workspace work bounded by the requested page plus a documented
   constant-size reconciliation window. The workspace must not walk every Loan Account page,
   re-evaluate every eligible row, or refetch each selected aggregate one at a time. Query ceilings
   must remain stable at 1, 21, and 101 mixed eligible/denied/incoherent rows.
4. Project S36/S37, initiation, CFC approve/reject, transfer-success, and advice actions only through
   the exact public mutation-owner authority, object-scope, maker-checker, assignment, permission,
   and current-evidence predicates. Every advertised action must be accepted for the same actor and
   unchanged row; every mutation-denied actor/row must receive no action and no count disclosure.
5. Complete the omitted executable matrices: all SAP evidence components and downstream consumers;
   1/21/101-row page contents/totals/out-of-range/stable ordering; action allow/deny parity; exact
   create/send/complete/transfer request bytes and stable keys; independent 400/403/409 surfaces;
   and MP14 explicit-id selection in both list orders at unit level.
6. Retain the 009L3 pending-only posting constraint, masked values, restored S42 tabs, and exact
   transfer-winner acceptance label. Avoid duplicate full-suite discovery where the exact label can
   reference the existing observable winner contract without layering a second discovered copy.

## Scope Boundaries
- `CR-012` remains the sole owner of the nine-state hosted Epic 009 UI flow and image-hash evidence.
  This slice supplies product correctness and focused unit/API coverage first.
- No Epic 010 schedule, ledger, repayment, interest, DPD, default, closure, or new UI styling.
- No SAP posting-confirmation actor, permission, adapter, or success evidence may be invented under
  A-135; the initial-payment obligation remains pending-only.

## Acceptance and Reverse-Consumer Tests
- The retained review probe turns green: a newer incoherent cross-application completion makes both
  member and account decisions unavailable, and the same result propagates to every consumer.
- Mixed portfolios at 1, 21, and 101 rows prove truthful full pages, totals, navigation,
  out-of-range behavior, nondisclosure, deterministic ordering, and stable query ceilings for both
  Loan Account and staff-workspace collections.
- Full role/permission/governed-authority/task/assignment/maker-checker/current-evidence matrices
  pair every projected action with the corresponding public mutation allow/deny outcome.
- Existing transfer/posting winner tests, Loan Account detail/list, readiness, workspace, portal, and
  frontend tab tests remain green; the focused transport and MP14 opposite-order unit gaps close.

## Risk Level
High

## Acceptance Criteria
- Every Epic 009 consumer uses one canonical SAP completion truth and fails closed on the same drift.
- Eligible counts/pages are correct and portfolio growth does not multiply full evidence scans.
- Server-owned actions exactly match their mutation owners, with executable negative matrices.
- Epic 009 product truth is green before `CR-012` records final hosted UI evidence.

## Done Checklist
- [ ] Execution plan and impact boundary written
- [ ] Backend/business RED-GREEN evidence saved
- [ ] Canonical SAP decision and bounded selectors implemented
- [ ] Pagination, action-parity, transport, and opposite-order matrices green
- [ ] Focused reverse-consumer and configured gates passed
- [ ] Risk/review evidence completed; commit delegated to Ralph
