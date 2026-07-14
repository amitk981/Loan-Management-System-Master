# Slice 007T: Register Null Contract and Action Order Closure

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Depends On
- 007S

## Runtime Capabilities

- `localhost-e2e-server`

## Goal

Make the S23 frontend consume the exact legacy-null register contract and keep a post-action detail
refresh from replacing a newer S21 page/filter state.

## Source / Review References

- `docs/source/screen-spec.md` S21 and S23
- `docs/source/api-contracts.md` §§6.2, 8.1, 25.3, and 25.9
- `docs/source/codebase-design.md` §§23.3-23.5, 26.1-26.3, and 42.3
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/slices/007R-legacy-approval-history-and-frozen-identity-closure.md`
- `docs/slices/007S-register-pattern-and-pagination-order-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-14_093142_architecture_review`

## Concrete Requirements

1. Align `CreditSanctionRegisterRow` with the real backend legacy contract: `purpose` and `risk`
   may each be null. The S23 detail must render the existing unavailable-value treatment without a
   property dereference, error boundary, live reconstruction, or fabricated empty object.
2. Replace the legacy component and trusted-browser fixtures with the exact API shape produced for
   a pre-007O/pre-007Q row: top-level `purpose: null`, `risk: null`, nullable folio/loan type,
   empty approver arrays, and null terminal/communication facts. Keep every non-null modern field
   and the existing table/detail composition unchanged.
3. Put action submission, its detail refetch, optional sanction-decision refetch, and queue-row
   replacement behind the same S21 request generation authority as page/filter/detail reads. If a
   newer page, filter, denial, malformed response, or empty state starts while an action refresh is
   pending, the older result may report the action outcome but must not replace current collection,
   total, selection, detail, decision, error, or empty state.
4. Make every S21 component pagination fixture internally valid. A non-final page of size 20 must
   contain 20 rows; focused ordering tests may instead use a page size/total combination whose exact
   row count is represented. Do not bypass `authenticatedPaginatedRequest` validation with states
   the production transport rejects.
5. Preserve backend actor/object scope, immutable v2/v3 history, strict shared pagination, all
   007S browser outputs, and the fixed prototype styling. This is a contract/order correction, not
   a register redesign.

## Trusted Browser Acceptance

- Spec: `e2e/sanction-workbench.e2e.spec.ts`
- Spec: `e2e/approval-register-settings.e2e.spec.ts`
- Screenshot: `sanction-action-filter-race.png`
- Screenshot: `credit-sanction-register-legacy-null.png`

## Trusted Browser Scenario

Return an exact legacy S23 row with top-level null purpose/risk and select it through the production
shell; the complete unavailable-value detail must remain visible without a page error. Separately,
delay the detail/decision refresh after an approval action, move to a newer server filter, release
the old response, and prove the new queue/total/detail remains authoritative.

## Test Cases

- Component and browser tests consume the exact backend legacy row and assert purpose/risk render
  unavailable without live requests or a React exception.
- Delayed action POST/detail/decision outcomes across newer success, denied, malformed, and empty
  filter states cannot overwrite the newest state.
- All page-one/middle/final/empty fixtures satisfy exact shared pagination counts and still exercise
  previous/next/filter transitions.
- Existing modern S23/S25 source evidence, nullable approver identity, and no-download behavior stay
  intact.

## Evidence Required

Frontend RED/GREEN output, exact backend-to-frontend fixture trace, trusted-browser collection and
two-run outputs, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- A real legacy register response cannot crash or fabricate S23 facts.
- A stale post-action refresh cannot replace newer S21 authority.
- All UI pagination fixtures are production-valid and all configured gates pass.

