# Slice 006Z8: Portal Limit Provenance, Module, and Interaction Closure

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review

## Depends On
- 006Z7

## Runtime Capabilities
- `localhost-e2e-server`

## Goal

Keep unchanged verified authority valid across dates, move borrower-limit orchestration behind the
credit module boundary, and close the real submit/refetch/error/browser contract.

## Source / Review References

- `docs/source/functional-spec.md` BR-003 through BR-007 and M04-FR-005 through M04-FR-007
- `docs/source/api-contracts.md` §6-§8 and §22-§24
- `docs/source/codebase-design.md` §22.1, §26.1-§27.1, §42.1-§42.3
- `docs/slices/006Z2-portal-application-limit-display-authority.md`
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_004501_architecture_review`

## Concrete Requirements

1. Validate current effective authority from its stored calculation date/result/snapshot and current
   evidence provenance. Do not recalculate with today's date and invalidate an otherwise unchanged
   record merely because `calculated_as_of_date` participates in `result_id`. Future, closed, stale,
   manual, and provenance-mismatched records remain unavailable.
2. Move verified authority, share/land selection, effective-policy resolution, lower-limit math, and
   advisory derivation behind one credit-owned borrower-limit projection interface. The members
   portal service may resolve PortalAccount scope and redact/transport the returned projection only.
3. Reuse the page's existing money formatter and inline/existing visual compositions. Do not retain
   an unjustified new exported view component or duplicate currency formatter.
4. Map authoritative submit validation, including `required_loan_amount`, to the visible field/error
   state. A successful submit performs exactly one canonical projection GET; 400/403/409 perform no
   retry or local response merge. Remove the hard-coded initial projection argument in favor of the
   actual controlled requested amount.
5. Mount the routed real portal container and prove exact request method/URL/body, server-only three
   amounts/advisory, unavailable/loading/error states, conflicting submit/projection values, retained
   provenance after reload, and absence of IDs/evidence/staff actions.
6. Preserve the approved three green cards, existing red advisory, and review maximum with no new
   styling, layout, typography, colour, or client money/authority calculation.

## Trusted Browser Acceptance

- Spec: `e2e/portal-application-limit-authority.e2e.spec.ts`
- Screenshot: `portal-limit-available.png`
- Screenshot: `portal-limit-unavailable.png`
- Screenshot: `portal-limit-over-limit-advisory.png`
- Screenshot: `portal-limit-review-maximum.png`
- Two independent real-login runs must pass with collision-safe data and identical response redaction.

## Test Cases

- Yesterday's unchanged current effective authority remains available today; changed evidence and
  future/closed records are unavailable.
- Public portal adapter delegates to the credit projection and contains no loan-limit orchestration.
- Routed success submits once and refetches once; 400/403/409 preserve server field errors with no retry.
- Static regression finds no client limit arithmetic, duplicate formatter, hard-coded projection
  request, new visual styling, or leaked internal authority facts.

## Evidence Required

Failing next-day/module-boundary/submit-error tests; green backend and mounted interaction matrices;
browser collection; two trusted runs with all screenshots; dependency scan; and all configured gates.

## Risk Level
High

## Acceptance Criteria

- The borrower limit remains current by evidence provenance rather than wall-clock hash drift.
- Credit owns all limit decisions; the portal adapter/UI only scopes, redacts, requests, and renders them.

## Run-Ahead Sharpening Review (006Y15, 2026-07-13)

- Confirmed execution-ready against the already-open backend/frontend review rules: credit owns the
  decision, the portal transports and renders it, and every named response state has an exact
  interaction contract.
- Preserve the declared existing compositions and trusted-browser outputs; no new visual pattern or
  caller-owned authority switch is permitted.
