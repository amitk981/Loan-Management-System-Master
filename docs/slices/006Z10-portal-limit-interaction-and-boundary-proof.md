# Slice 006Z10: Portal Limit Interaction and Boundary Proof

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review

## Depends On
- 006Z8
- 006Z9

## Runtime Capabilities
- `localhost-e2e-server`

## Goal

Prove the credit-owned borrower-limit projection through every blocked boundary and the real portal
submit lifecycle, so rendering-only fixtures can no longer claim submit/refetch/error closure.

## Source / Review References

- `docs/source/functional-spec.md` M04-FR-005 through M04-FR-007
- `docs/source/api-contracts.md` §§6-8 and §§22-24
- `docs/source/codebase-design.md` §§22.1, 23.3, 26.1-27.1, and §§42.1-42.3
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/slices/006Z8-portal-limit-provenance-module-and-interaction-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-13_025409_architecture_review`

## Concrete Requirements

1. Add public credit-projection cases for future/closed/manual/stale/mismatched authority, changed
   supply/service provenance, duplicate shareholdings, missing/contradictory land/profile facts,
   no effective policy, and invalid requested amount. Each returns the stable redacted envelope or
   validation error without leaking identifiers/evidence or writing state.
2. Mount the routed MP05 container and submit through the actual draft/create-or-update and submit
   adapters. Assert exact request method/URL/body, exactly one successful submit, and exactly one
   canonical post-submit projection GET using the returned authoritative amount.
3. Execute 400 field validation (including `required_loan_amount`), 403, and 409 separately; show the
   authoritative visible error, preserve entered values, and perform no retry, local response merge,
   or projection refetch.
4. Prove loading, unavailable, transport error, conflicting server requested/final amounts, retained
   stored-date provenance after reload, and redaction through observable UI behavior.
5. Strengthen the browser scenarios so server-flag authority is discriminating: include a requested
   amount above the maximum with `exception_required_flag = false`, then the inverse, and prove the
   advisory follows only the flag. At least one trusted scenario executes submit/refetch and reload.
6. Replace raw source/fixture-name assertions where equivalent public behavior can prove the rule;
   retain only the narrow static checks needed to forbid client money arithmetic or new styling.

## Trusted Browser Acceptance

- Spec: `e2e/portal-application-limit-authority.e2e.spec.ts`
- Screenshot: `portal-limit-available.png`
- Screenshot: `portal-limit-unavailable.png`
- Screenshot: `portal-limit-over-limit-advisory.png`
- Screenshot: `portal-limit-review-maximum.png`

## Test Cases

- Success create/update + submit + one canonical refetch, with exact interaction trace.
- Independent 400/403/409 rows with visible errors and zero refetch/retry.
- Contradictory amount/flag fixtures prove there is no client recomputation.
- Reload retains the backend projection and exposes no internal authority fact.

## Evidence Required

Failing mounted submit/error and discriminating-advisory tests; green backend boundary matrix;
browser collection; two trusted runs with all screenshots; and all configured gates.

## Risk Level
High

## Acceptance Criteria

- The real portal lifecycle—not source strings or rendering-only fixtures—proves submit and error behavior.
- Every financial decision remains credit-owned, redacted, and server-authored.
