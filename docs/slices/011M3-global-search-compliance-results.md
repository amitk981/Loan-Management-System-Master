# Slice 011M3: Global Search Compliance Results

## Status
Complete

## Runtime Capabilities
- `localhost-e2e-server`

## Parent Epic
Epic 011: Default, Recovery, Closure, NOC, Archive, and Compliance
Epic file: `docs/epics/011-default-recovery-closure-compliance.md`

## Origin
The final queue review found that 010N was scheduled before the 011K–011M compliance records it
promised to search. This successor closes S02 only after those canonical owners exist.

## Goal
Register the seventh S02 Global Search group over real compliance records and prove the complete
seven-group search contract without moving, copying, or weakening the 010N privacy boundary.

## User Value
Authorised Compliance, CFO, CS, and Internal Auditor users can find governed compliance work from the
same global search while other roles learn nothing about restricted records or match existence.

## Depends On
- 010N
- 011M

## Trusted Browser Acceptance
- Spec: `e2e/global-search.e2e.spec.ts`
- Screenshot: `global-search-compliance-results.png`

## Source References
- `docs/source/screen-spec.md` S02 result grouping, result-card fields, quick actions, and permissions
- `docs/source/api-contracts.md` §8.4 search conventions and §8.1 pagination
- `docs/source/auth-permissions.md` compliance, evidence, report, and auditor read scopes
- `docs/source/security-privacy.md` compliance evidence and sensitive search minimisation
- `docs/slices/010N-global-search-api-and-ui.md` registered provider/privacy/result-card contract
- `docs/slices/011K-compliance-control-tracker-foundation.md`
- `docs/slices/011L-section-186-and-nbfc-test-trackers.md`
- `docs/slices/011M-kyc-re-kyc-compliance-tracker.md`

## Prototype Reference
- `sfpcl-lms/src/pages/search/GlobalSearchResults.tsx`

## Backend/API Scope
- Implement the 010N compliance provider through canonical 011K control/task/evidence and
  money-lending records, 011L Section 186/NBFC results, and 011M KYC/re-KYC reviews. Reuse their
  selectors and identifiers; do not add a cross-domain search table or recompute compliance state.
- Return only role/object-scoped, paginated, deterministically ordered projections. Restricted
  evidence text/files, KYC values, legal opinions, internal notes, and hidden counts never enter the
  search response, logs, audit payloads, or browser cache.
- Map every result to the S02 card contract: safe title and visible identifier, status/risk,
  applicable amount only when source-backed, current owner, last-updated actor/date, and only the
  quick actions the caller can actually perform.
- Register the provider fail-closed: an unavailable owner or unresolved permission mapping produces
  a safe group error/omission, never broad fallback access or fabricated empty success.

## Frontend Scope
- Render the Compliance records group in the existing 010N screen with existing grouped-result,
  loading, partial-error, empty, and unauthorised patterns; add no styling or separate search index.
- Preserve 010N sensitive-query handling and remove no permission check to make a screenshot pass.

## Test Cases
- Every canonical 011K–011M record type maps to the correct safe card and opens only an authorised
  existing route; totals/order/pagination reconcile with source-owner selectors.
- Cross-role, cross-scope, guessed identifier, restricted evidence/KYC/legal content, hidden count,
  unavailable provider, and invalid quick-action tests fail without leakage.
- Complete S02 matrix proves all seven groups, all required card fields, permission-filtered quick
  actions, and all 15 010N search inputs with no local sensitive index.

## Evidence Required
Saved RED/GREEN provider/API/frontend output; source-to-card/permission matrix; leak-negative and
reverse-consumer evidence; complete S02 matrix; the declared screenshot from two trusted browser
runs; 010N and compliance focused regressions plus configured full gates.

## Risk Level
High

## Acceptance Criteria
- S02 returns all seven source-required groups only after their canonical data owners exist.
- Compliance search is reconciled, permission-correct, masked, and cannot expose restricted evidence
  or match existence.
- Required focused, browser, reverse-consumer, and full gates pass.

## Done Checklist
- [ ] Execution plan and TDD evidence saved
- [ ] Compliance provider/API/UI contract implemented
- [ ] Complete S02 and permission/leak matrices passed
- [ ] Trusted browser evidence passed twice
- [ ] Full gates and risk review passed
- [ ] Commit delegated to the orchestrator after gates
