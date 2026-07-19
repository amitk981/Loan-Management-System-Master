# Slice 010L: Member Portal Repayment View

## Status
Not Started

## Parent Epic
Epic 010: Servicing, Repayments, Interest, and Monitoring
Epic file: `docs/epics/010-servicing-repayments-interest-monitoring.md`

## Goal
Provide borrower-safe own-loan projections and wire MP15–MP18 to real account, schedule, verified
repayment, interest-invoice, and approved direct-repayment-instruction truth.

## User Value
An authenticated member can understand their current loan and confirmed repayments without seeing
another borrower or internal finance/SAP data.

## Depends On
- 010K2

## Runtime Capabilities

- `localhost-e2e-server`

## Trusted Browser Acceptance

- Spec: `e2e/member-portal-repayment-view.e2e.spec.ts`
- Screenshot: `member-portal-repayments-populated.png`
- Screenshot: `member-portal-repayments-empty.png`
- Screenshot: `member-portal-repayments-error.png`
- Screenshot: `member-portal-repayments-mobile.png`

## Source References
- `docs/source/screen-spec-member-portal.md` MP15–MP18, §§8.6, 9, 14.5, 15
- `docs/source/product-requirements.md` §11.21
- `docs/source/auth-permissions.md` §§19.3, 20.2 (`borrower_self`)
- `docs/source/api-contracts.md` §§30, 32–33 (source data; define separate portal projections)
- `docs/source/security-privacy.md` §22
- `docs/source/test-plan.md` §§16.11–16.13, 20.2–20.3
- `docs/working/digests/epic-010-servicing-repayments-interest-monitoring.md` §010L

## Prototype Reference
- `sfpcl-lms/src/pages/borrower/portal/loans/MP15_MyLoans.tsx`
- `sfpcl-lms/src/pages/borrower/portal/loans/MP16_LoanAccountDetail.tsx`
- `sfpcl-lms/src/pages/borrower/portal/loans/MP17_Repayments.tsx`
- `sfpcl-lms/src/pages/borrower/portal/loans/MP18_DirectRepaymentInfo.tsx`

## Concrete Requirements
1. Define borrower-safe `/api/v1/portal/loan-accounts/` list/detail projections and bounded schedule,
   repayment-history, invoice-summary, and direct-instructions shapes in the repository API contract.
   Reuse canonical 010A–010K services; do not expose staff serializers directly.
2. Resolve the member only from the authenticated portal principal. Ignore/reject caller-supplied
   member identity and return not-found-safe behavior for another member's account, schedule, receipt,
   invoice, statement, acknowledgement, or document.
3. MP15 shows active/closed own accounts with borrower-safe status, amount, next due, and routes to the
   explicitly selected account. MP16 shows summary, balances, schedule, verified history, invoice/
   notices, and closure status without client-side account selection/ranking.
4. MP17 shows only internally verified/posted repayment truth, principal/interest split where allowed,
   reference/acknowledgement, and `Under verification` only when an approved borrower-proof feature
   exists. Unmatched internal bank lines are never exposed as confirmed payments.
5. MP18 shows only approved repayment account details, masked where required, required narration, due
   amount, and the source disclaimer. Keep UTR/proof submission disabled unless an existing approved
   configuration and contract already enable it; read-only delivery still completes this slice.
6. Remove runtime mocks/inline business fixtures from MP15–MP18 and their route/service path. Preserve
   existing portal shell/patterns, Money formatting, mobile layout, and loading/empty/error/unauthorised
   states. Never expose internal actor IDs, SAP notes, full bank details, exception notes, or provider data.

## Scope Boundaries / Non-Goals
- No staff servicing screens (`010M`), payment initiation/gateway, automatic matching, default actions,
  grievance implementation, NOC/closure work, or unapproved borrower UTR/proof submission.
- Member Portal MVP inclusion remains an open product decision; implement only this already-queued,
  access-safe capability without broadening portal policy.

## Acceptance and Reverse-Consumer Tests
- Owner sees exact MP15–MP18 account/schedule/posted-repayment/invoice truth and approved instructions;
  balances match staff owner APIs without browser calculation.
- Other member, staff token, missing/locked portal account, caller-supplied member ID, guessed UUID, and
  nested foreign receipt/invoice/document all fail without existence or data leakage.
- Pending/unmatched/failed receipts do not appear as confirmed; later verified posting becomes visible
  through canonical state only.
- Regression/static tests prove MP15–MP18 and services have no `mockData`/inline business reads; existing
  portal authentication, application, documentation, and MP14 disbursement views remain green.
- Frontend covers populated, empty, loading, API error, unauthorised, long ledger, and narrow viewport.

## Visual Acceptance Criteria
Use existing portal components and spacing only. MP15 list, MP16 detail, MP17 repayment history, and
MP18 instructions remain readable at the trusted borrower viewport with no horizontal financial-table
loss and clear backend-error/empty states.

## Evidence Required
- RED/GREEN portal projection/object-access/API tests, exact service URL/payload frontend tests, mock
  removal proof, safe response examples, focused 010A–010K and existing portal regressions, and trusted
  browser screenshots for populated/empty/error plus mobile MP17/MP18 states.

## Risk Level
High

## Acceptance Criteria
- MP15–MP18 consume real backend truth for only the authenticated member and expose no internal or
  foreign financial data.
- Only verified/posted repayments appear as confirmed and runtime mock surface is zero.
- Required focused, access-control, visual, reverse-consumer, and full gates pass.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested, if needed
- [ ] Audit events tested, if needed
- [ ] Visual evidence saved, if frontend
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Substantive risks/decisions recorded in `review-packet.md` (and HANDOFF only when needed)
- [ ] Commit created only after passing gates
