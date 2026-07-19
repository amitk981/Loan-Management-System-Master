# Slice 009L5: Epic 009 Exact Selector and Consumer Parity Closure

## Status
Complete

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Make Epic 009 collection identities, pagination totals, and every SAP completion consumer use the
same exact owner decisions, so stale or incoherent evidence cannot disclose a row, shift a page, or
advance one application using another application's completion.

## Depends On
- 009L4

## Runtime Capabilities

- `none`

## Source / Review References
- `docs/source/functional-spec.md` M07-FR-010 and M08-FR-003, M08-FR-006
- `docs/source/api-contracts.md` §§29-31 and 45
- `docs/source/auth-permissions.md` §§19.3, 25.7, 26.5, and 34.7
- `docs/source/codebase-design.md` §§16, 26, and 42
- `docs/working/API_CONTRACTS.md` Loan Account 360 and staff-workspace contracts
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-19_123045_architecture_review`
- `.ralph/runs/2026-07-19_123045_architecture_review/evidence/review-probes/test_009l4_selector_contract_probes.py`

## Concrete Requirements
1. Define one exact eligible-identity decision for Loan Account reads and one for each S36, S37,
   Senior Finance, and CFC workspace branch. Count, total pages, page offsets, and projected rows
   must consume that exact decision; a broader queryable candidate set must not be reported as the
   final total.
2. Preserve database pagination and bounded work without relying on a four-row overscan to repair
   false positives before the requested offset. Evidence-incoherent rows affect neither totals nor
   reachability, even when more than the reconciliation window occur before or within a page.
3. Make every SAP-dependent consumer, including member, account, readiness, workspace, Loan Account,
   disbursement, and member-portal stage projection, validate the same member/application/customer-
   code edge. A coherent completion for another application must not satisfy M07-FR-010 for the
   requested application, including when the member reuses the same customer code.
4. Keep lifecycle creation, SAP completion, transfer, initiation, and action authority rules behind
   their public owners. Remove the duplicated scalar lifecycle-evidence validator or make one
   implementation the sole source used by both exact single-row and bounded bulk decisions.
5. Complete the retained executable matrix: Loan Account and every staff-workspace branch at 1, 21,
   and 101 mixed eligible/denied/incoherent rows; more than four consecutive drifted rows; first,
   middle, last, and out-of-range pages; all SAP consumers; action/mutation allow-deny parity; and
   independent 400/403/409 surfaces. Assertions must include exact totals, page contents, stable
   ordering, nondisclosure, and query ceilings.
6. Turn all five retained architecture-review probes green, retain MP14 explicit-id behavior, and
   replace test setup that copies Django private `_state` where the public module/factory seam can
   create the same observable portfolio.

## Scope Boundaries
- `CR-012` remains the sole owner of hosted nine-state Epic 009 browser/image-hash evidence and
  executes only after this product-correctness closure.
- No Epic 010 repayment, interest, ledger, DPD, default, or closure behavior.
- No SAP posting-confirmation actor, adapter, permission, or success evidence under A-135.
- No new styling or frontend component; only a member-portal consumer correction and its tests if
  required by the canonical application edge.

## Acceptance and Reverse-Consumer Tests
- Each retained probe reports `total_count == 0` and an empty page after non-queryable creation,
  completion, send, or initiation evidence drift.
- A latest coherent completion for another application, including reuse of the same customer code,
  leaves the requested application's portal SAP stage incomplete and blocks downstream readiness.
- Mixed portfolios at 1, 21, and 101 rows prove exact Loan Account and S36/S37/Senior Finance/CFC
  pagination with stable query ceilings and more than four adjacent false candidates.
- Every advertised action succeeds for the same actor and unchanged row with valid input; every
  mutation-denied actor/row receives no action and no count or page disclosure.
- Existing Epic 009 creation, readiness, transfer, advice, portal, and frontend tests remain green.

## Risk Level
High

## Acceptance Criteria
- Exact owner decisions, totals, page reachability, and projections cannot disagree.
- No Epic 009 consumer treats another application's SAP completion as current for its own edge.
- Portfolio growth and evidence drift do not multiply full scans or leak row existence.
- The full executable matrix closes before real-Django browser evidence or Epic 010 begins.

## Done Checklist
- [ ] Execution plan and impact boundary written
- [ ] Backend/business RED-GREEN evidence saved
- [ ] Exact selectors and canonical consumer edge implemented
- [ ] Pagination, consumer, action, transport, and error matrices green
- [ ] Focused reverse-consumer and configured gates passed
- [ ] Risk/review evidence completed; commit delegated to Ralph
