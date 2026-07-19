# Slice 009L: Epic 009 Staff Workflow and SAP Posting Closure

## Status
Complete

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Close Epic 009 with a genuinely walkable S36-S41 staff workflow, exact current workspace authority
and evidence, the missing initial-loan-payment SAP posting truth, and the browser/regression evidence
that 009I2, 009J, and 009K declared but did not retain.

## Depends On
- 009K

## Runtime Capabilities

- `localhost-e2e-server`

## Source / Review References

- `docs/source/functional-spec.md` M07-FR-001 through M07-FR-010 and M08-FR-001 through M08-FR-011
- `docs/source/screen-spec.md` S36-S42 and §9.6
- `docs/source/api-contracts.md` §§29-31 and 45
- `docs/source/auth-permissions.md` §§12.9, 15.6-15.7, 16.3, 19.3, 25.7, 26.5, and 34.7
- `docs/source/codebase-design.md` §§16, 26, 34-35, 40, and 42
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/slices/009I2-portal-disbursement-stage-and-visual-closure.md`
- `docs/slices/009J-loan-account-360-initial-view.md`
- `docs/slices/009K-disbursement-and-cfc-frontend-wiring.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-19_041708_architecture_review`
- `.ralph/runs/2026-07-19_041708_architecture_review/evidence/review-probes/test_epic009_closure_probes.py`

## Concrete Requirements

1. Add a canonical, permission- and object-scoped S36 candidate/assignment projection for Credit
   Manager. Project server-owned create/send actions through the exact 009A/009B public owners, with
   safe assignee choices and fixed application/member facts; never accept a free-form raw id or
   expose PAN, Aadhaar, full bank/SAP values, workbook storage, or internal evidence ids.
2. Derive every workspace row and action from the public owner that executes it. A stale, duplicate,
   changed, cross-object, or otherwise incoherent SAP/disbursement/transfer/advice tuple is omitted
   or rendered as a safe blocker and advertises no action. Replace direct SAP-model reads and local
   reconstruction in the cross-owner process/read modules with the canonical SAP facade.
3. Enforce exact current effective authority before projecting an action. CFC reads require a
   governed active CFC authority, the current task relation, and `finance.disbursement.authorise`;
   SAP completion uses the real `finance.sap_request.complete` permission and exact assignee/state.
   A missing dependent permission returns the standard 403/empty scoped result, never an uncaught
   500. Optional SAP completion fields remain optional.
4. Convert every `datetime-local` browser value to a timezone-aware ISO-8601 instant before calling
   SAP completion or transfer success. Add transport-level tests asserting the exact request bytes,
   timezone, fixed payload, stable idempotency key, and visible 400/403/409 behavior; mocked service
   success alone is insufficient.
5. Implement M07-FR-009 as one durable initial-loan-payment SAP posting obligation tied to the exact
   successful-transfer aggregate. It starts honestly pending and retains amount, loan/application,
   transfer/register evidence, created time, and safe posting status/reference. If the source does
   not name the posting actor or external adapter, keep confirmation behind an explicit unassigned
   grant/configured adapter and record the open governance fact; never claim SAP success from local
   payment or a mutable label.
6. Make Loan Account list/search honor the source-defined §30.2 filters that are supported by current
   owner truth; explicitly defer `dpd_bucket` to its Epic 010 owner rather than classifying a named
   source parameter as unknown. Keep selectors query-bounded and paginate in the database before
   per-row composition; add populated query-count evidence for both staff collections.
7. Complete the declared negative matrices: 009J creation/terms/SAP/transfer/activation/register/
   advice/balance drift, 009K role/permission/authority/current-evidence action parity, and MP14 two
   finance-relevant applications in opposite list orders through unit and real-browser selection.
   Keep 010M-owned repayment/interest/default/closure tabs unavailable or explicitly fixture-labelled
   so real account identity is never composed with another borrower's mock financial history.

## Trusted Browser Acceptance

- Spec: `e2e/epic-009-staff-disbursement-closure.e2e.spec.ts`
- Screenshot: `loan-account-sanctioned-summary.png`
- Screenshot: `loan-account-active-summary.png`
- Screenshot: `sap-request-and-confirmation.png`
- Screenshot: `disbursement-readiness-blockers.png`
- Screenshot: `payment-initiation.png`
- Screenshot: `cfc-authorisation.png`
- Screenshot: `transfer-and-advice-success.png`
- Screenshot: `loan-account-safe-error.png`

## Test Cases

- Run the S36 create/send and S37 completion path with real Django state; prove exact authority,
  redaction, assigned-user selection, optional fields, aware timestamps, and replay/denial behavior.
- For Senior Finance, CFC, Credit Manager, permission-only, role-only, inactive, revoked-authority,
  cross-scope, and stale-ledger actors, compare projected rows/actions with the public mutation
  owner's allow/deny decision and assert no 500 or zero-write authority widening.
- Reproduce both retained review probes: a valid Senior Finance workspace request never crosses an
  uncaught internal permission, and an incoherent approved disbursement is not projected as current.
- Successful transfer atomically creates one pending SAP posting obligation; exact replay and races
  retain one row, while changed/cross-object evidence creates none. Posting confirmation, if
  enabled, requires the explicit governed grant and immutable provider/manual evidence.
- Execute S36-S41 against real backend endpoints, including naive-time regression, duplicate UTR,
  idempotent initiation/transfer/advice replay, readiness blockers, and all eight screenshots twice.

## Database / Migration Impact

At most one Epic 009 owner migration for the M07-FR-009 posting obligation and protected singular
relation to successful transfer. Do not reuse Epic 010 repayment-posting rows or fabricate external
SAP acceptance.

## Risk Level
High

## Acceptance Criteria

- Every S36-S41 action is reachable, role-correct, current-evidence-backed, and accepted by its real
  endpoint; no UI control can be built from a stale label, wrong permission, or naive timestamp.
- M07-FR-009 has durable honest pending/posted truth without inventing external success or authority.
- Epic 009's declared unit, negative-matrix, real-backend browser, and visual evidence is complete,
  while later servicing truth remains owned by Epic 010.

## Done Checklist
- [ ] Execution plan written
- [ ] TDD red/green evidence saved
- [ ] S36-S41 and SAP posting closure implemented
- [ ] API contracts/assumptions/digest updated
- [ ] Permission, evidence-drift, redaction, pagination, and query-count tests passed
- [ ] Trusted browser contract passed twice with all screenshots
- [ ] Focused reverse-consumer and configured gates passed
- [ ] Risk and review evidence completed
- [ ] Commit delegated to the orchestrator after gates
