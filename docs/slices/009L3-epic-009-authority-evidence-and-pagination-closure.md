# Slice 009L3: Epic 009 Authority, Evidence, and Pagination Closure

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Close the remaining Epic 009 product boundary at the canonical owner seams: exact SAP/CFC action
authority, immutable SAP completion truth, truthful pre-pagination scope, pending-only initial SAP
posting governance, and the retained negative/UI contracts that 009L did not execute.

## Depends On
- 009L

## Runtime Capabilities

- `postgresql-five-race-acceptance`
- `localhost-e2e-server`

## Trusted PostgreSQL Acceptance

- Test: `sfpcl_credit.tests.test_epic009_postgresql_acceptance.Epic009BoundaryPostgreSQLAcceptanceTests`
- Expected tests: 2

## Trusted Browser Acceptance

- Spec: `e2e/epic-009-authority-evidence-pagination-closure.e2e.spec.ts`
- Screenshot: `loan-account-tabs-unavailable.png`
- Screenshot: `mp14-opposite-order-selection.png`

## Source / Review References

- `docs/source/functional-spec.md` M07-FR-001 through M07-FR-010 and M08-FR-001 through M08-FR-011
- `docs/source/screen-spec.md` S36-S42 and §9.6
- `docs/source/api-contracts.md` §§29-31 and 45
- `docs/source/auth-permissions.md` §§16.3, 19.2-19.3, 20.1, 25.7, 26.5, and 34.7
- `docs/source/codebase-design.md` §§16, 26, 31.4, and 42
- `docs/working/API_CONTRACTS.md` Loan Account 360 and staff-workspace contracts
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-19_093632_architecture_review`
- `.ralph/runs/2026-07-19_093632_architecture_review/evidence/review-probes/test_009l_contract_probes.py`

## Concrete Requirements

1. Make S36/S37 candidate selection a public SAP-owner selector that uses the same application
   authority and mutation predicate as create/send/complete. Every Credit Manager accepted by the
   public create owner can reach the row/action; intake creator/receiver fields cannot narrow the
   source-defined Credit Manager domain. Duplicate, stale, cross-scope, or incoherent requests are
   omitted or safe-blocked without exposing protected SAP or identity facts.
2. Project CFC authorise/reject actions only when the exact current mutation owner would accept the
   actor: active effective CFC role, governed `approval_authority_type`, Critical permission, exact
   current task/object relation, and current initiation evidence. Primary role or permission alone
   must produce no row/action and no existence/count disclosure.
3. Replace `get_account_customer_code`'s parallel reconstruction with the canonical SAP completion
   evidence decision. Blank, changed, duplicated, cross-application, stale-assignee, audit/workflow,
   input-digest, code-identity, or send-evidence drift must be rejected identically by member,
   account, readiness, workspace, and Loan Account reads. Return masked SAP values only.
4. Apply role/object scope and immutable-evidence eligibility before count and database pagination.
   Loan Account and staff workspace pages must have truthful totals, full stable pages when enough
   eligible rows exist, no stranded later rows, and no unauthorized/incoherent count leakage. Do
   not walk all account pages or compose every row before slicing; query work must remain bounded as
   eligible portfolio size grows.
5. Under A-135, an initial-loan-payment SAP obligation is `pending` only. Database constraints,
   serializers, and current-success coherence must reject a locally fabricated `posted` status
   until a future governed slice adds the named actor, permission, adapter, and immutable provider/
   manual acceptance evidence. Do not treat a mutable reference and timestamp as SAP success.
6. Restore the established Loan Account 360 shell/tab layout using existing components and styling.
   Keep 010M-owned repayment, interest, monitoring, default, and closure bodies explicitly
   unavailable without mock rows or client calculations; do not replace the approved layout with a
   new facts-grid design.
7. Complete the executable matrices omitted by 009L: creation/terms/SAP/transfer/activation/
   register/advice/balance drift; role/permission/governed-authority/task/current-evidence action
   parity; 21/101-row mixed-scope pagination; S36 create/send/complete and transfer transport
   payload/error interaction; and MP14 two finance-relevant applications in opposite orders through
   both unit and real-browser selection.

## Test Cases

- Convert all three retained review probes to current product regressions and add the paired public
  mutation allow/deny assertion for every projected S36/S37/CFC action.
- With valid rows before and after denied/incoherent rows, prove page contents, totals, next/previous,
  out-of-range behavior, stable ordering, nondisclosure, and query ceilings at 1, 21, and 101 rows.
- Drift each SAP completion evidence component independently and prove every downstream facade/read
  fails closed; no raw customer code or internal evidence identity is serialized.
- Database and service tests reject evidence-free `posted`; successful transfer, exact replay, and
  five-way PostgreSQL contention explicitly assert one pending posting row and no second aggregate.
- Frontend unit tests submit create/send/complete/transfer, assert exact aware bytes and stable keys,
  and display 400/403/409 without optimistic success. Browser proof selects MP14's explicit id in
  both opposite orders and captures the restored unavailable-tab shell without fixtures.

## Scope Boundaries

- `CR-012` owns the nine-state real-Django Epic 009 Playwright evidence/hashes after these product
  defects are corrected. Do not duplicate or weaken that contract here.
- No Epic 010 schedule, ledger, repayment, interest, DPD, default, or closure truth; no new visual
  system; no SAP confirmation actor/adapter invented; no production seed outside guarded E2E mode.

## Risk Level
High

## Acceptance Criteria

- Every projected action matches its public mutation owner's authority and evidence decision.
- Counts/pages disclose only eligible coherent rows, stay bounded, and cannot strand valid records.
- SAP completion and initial-payment posting truth cannot be promoted from mutable labels/references.
- The prototype layout is preserved without mock servicing facts, and the full negative/race/
  interaction matrix is executable before `CR-012` supplies final real-browser evidence.

## Done Checklist
- [ ] Execution plan and impact boundary written
- [ ] Backend/business RED-GREEN evidence saved
- [ ] Authority, evidence, pagination, pending-only posting, and UI contracts implemented
- [ ] PostgreSQL and browser contracts passed twice
- [ ] Focused reverse-consumer, frontend, and configured gates passed
- [ ] Risk/review evidence completed; commit delegated to Ralph
