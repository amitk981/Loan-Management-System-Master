# Slice 006Z2: Portal Application Limit Display Authority

## Status
Not Started

Interim owner fix applied 2026-07-11 (outside the Ralph loop): the client-side limit math (`shareholdingLimit`, hard-coded `landBasedLimit = 675000`, `Math.min`), the local submission gate, the red over-limit warning, and the review-step "Maximum Limit" row were removed from `MP05_NewApplication.tsx` and replaced with explicit "limit is determined during credit assessment" notes; regression tests added in `MP05_NewApplication.test.tsx`; typecheck/lint/tests/build all pass. This slice still owns the real deliverable: the borrower-scoped server limit-projection endpoint and its display (requirements 1, 2, and 4 below). Requirement 3 (server-driven advisory) also remains.

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review (portal corrective)
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Remove the client-side loan-limit calculation from the wired portal New Application screen. The 2026-07-11 audit found `MP05_NewApplication.tsx` (slice 005G, marked Complete) computes `shareholdingLimit = sharesHeld × valuationPerShare` (the source formula is shares × 30% of valuation — the displayed math is wrong), hard-codes `landBasedLimit = 675000`, takes `Math.min` locally, and gates submission eligibility on that local result.

## User Value
Borrowers see the same limit the backend will actually apply — served by the Epic 006 calculator/snapshot — instead of an incorrectly computed client-side figure that could invite or block applications wrongly.

## Depends On
- 006Z4

## Source References
- Final SOP - Loan Disbursement V10 (1).pdf p.10 §2.2-§2.3 (limit = lower of shares × 30% of valuation and per-acre scale of finance × cultivated land; ₹20,000/acre cap; ₹200/share current)
- docs/slices/006C-loan-limit-configuration-and-calculator.md and 006D (server-side calculator and snapshot — delivered)
- docs/slices/005G-member-portal-application-start-status.md (portal application contract)
- docs/source/screen-spec-member-portal.md new-application screen
- docs/working/FRONTEND_DESIGN_RULES.md mock-surface ratchet rule 3 (no server-owned money decisions client-side)

## Prototype Reference
- sfpcl-lms/src/pages/borrower/portal/applications/MP05_NewApplication.tsx (lines ~113-115, 158, 407-409, 462-465)

## Concrete Requirements
1. Add (or reuse, if 006C/006D already expose one adaptable to portal scope) a borrower-scoped read endpoint returning the member's current eligible-limit projection: shareholding-based limit, land-based limit, and the effective (lower) limit, computed server-side from 006C configuration and the member's real shares/landholding; own-data scope from PortalAccount.
2. Replace every local limit computation and the `landBasedLimit = 675000` constant in `MP05_NewApplication.tsx` with that response; the limit panel is display-only.
3. The client-side "requested amount within limit" submission gate becomes advisory display driven by the server response; the authoritative rejection stays the 005G/006 server validation, surfaced as a field error on submit.
4. Amounts render with the standard Money formatting; loading/error/unavailable states for the limit panel (a member without evaluable limit facts sees an explicit "limit not yet available" state, not a computed guess).
5. Regression: no arithmetic on shares/valuation/acreage remains in portal application code.
6. Restore the approved pre-interim three-card green limit composition once server projections are
   available: Shareholding Limit, Land-Based Limit, and Maximum Permissible Limit remain in the
   existing responsive grid and use the existing green card classes. The unavailable state must
   reuse that composition or an existing portal empty-state pattern; do not retain the interim
   one-column slate redesign.
7. A server-reported over-limit advisory uses the existing red alert composition, and the review
   step restores its Maximum Limit row from the server projection. Copy must say the request is
   subject to the configured exception/credit workflow; React must not promise an automatic block,
   reduction, or return that the source contract does not state.

## Owned Mock Removals
- `src/pages/borrower/portal/applications/MP05_NewApplication.tsx` — inline limit constants and client-side limit math removed.

## Test Cases
- Limit panel renders the server projection for the authenticated member; cross-member access blocked.
- Requested amount above the server limit: UI shows the server-driven warning and submit surfaces the backend validation error.
- No client-side limit arithmetic remains (static regression on the removed expressions).
- Member without limit facts sees the explicit unavailable state.
- Visual regression compares the server-backed panel, unavailable panel, advisory, and review row
  with the pre-interim prototype composition; no colour/layout/card change is accepted.

## Out of Scope
Limit formula/configuration changes (006C owns), staff calculator UI (006H owns), produce-supply persistence (006Z), application submission contract changes (005G owns).

## Risk Level
Medium

## Acceptance Criteria
- The portal shows only server-computed limits; the wrong-formula display and hard-coded land limit are gone with regressions.
- All gates pass; screenshots of the limit panel states saved.

## Run-Ahead Sharpening Review (006Y2, 2026-07-12)

- Mount the real portal application container in interaction tests. Assert one borrower-scoped
  projection GET, exact server amounts in all three existing cards, and no client recalculation or
  retry when the projection or submit endpoint returns 400/403/409.
- Trusted-browser screenshots must use the real portal login boundary and reopen the routed screen
  after reload; no plaintext member identity data may appear in fixtures, logs, or baselines.

## Run-Ahead Sharpening Review (006Y4, 2026-07-12)

- Keep the projection endpoint read-only and portal-account scoped; it returns no staff resource
  actions. Mounted tests must prove one projection GET and no retry/local synthesis after errors.

## Run-Ahead Sharpening Review (006Z, 2026-07-12)

- Reuse 006Z's PortalAccount-only service boundary and portal projection rule: no `member_id`,
  protected identity, or staff `available_actions` may appear in the limit response.
- A limit projection may consume only verified persisted member facts and effective 006C policy;
  unavailable or stale facts return an explicit server state, never a zero or client fallback.
- Keep requested-amount comparison server-owned and return the advisory as a projected fact so the
  mounted portal test can prove no arithmetic or inferred authority remains in React.

## Run-Ahead Sharpening Review (006Y6, 2026-07-12)

- Keep every limit/advisory state canonical after submission by refetching the borrower-scoped
  projection once; never merge the submitted amount into the projection or infer a warning locally.
- The mounted no-authority/error cases must prove no mutation/retry is invoked, while the three
  approved cards and review row consume only fields present in the server response.

## Run-Ahead Sharpening Review (006Z3, 2026-07-12)

- Resolve the borrower member only from the active `PortalAccount`, then consume
  `members.modules.active_member_status.ActiveMemberStatusResult`; do not query or reinterpret raw
  `ProduceSupplyRecord` rows inside the portal-limit endpoint.
- Treat `persisted_no_qualifying_verified_records` and continuity below four years as unavailable
  unless the shared result carries recorded relaxation/manual evidence. Pending, malformed-year,
  wrong-entity/route, and evidence-free rows must never become limit inputs or an apparent zero.

## Run-Ahead Sharpening Review (Architecture Review, 2026-07-12)

- Depend on 006Z4's dated, verified active-member result and immutable evidence snapshot. The portal
  limit endpoint may not calculate continuity, interpret service/employment years, or read raw supply
  rows; a result with a future-as-of date, incomplete continuity, or unverified/manual evidence is an
  explicit unavailable state.
- Mounted/browser assertions must prove the returned limit's active-member result date/version is
  retained after a canonical refetch and that no member identifier, row-level evidence reference, or
  staff verification action leaks into the borrower response.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated
- [ ] Permissions tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates

## Run-Ahead Sharpening Review (006Y11, 2026-07-12)

- Mount the routed portal container at the shared HTTP transport. A successful projection performs
  exactly one borrower-scoped GET and renders the canonical result date/version with all three money
  cards; 400/403/409 responses preserve exact server facts with no retry, local merge, or fallback.
- Trusted-browser data must be collision-safe across both independent executions and assertions must
  prove the response contains no member identifier, evidence reference, or staff action before capture.

## Run-Ahead Sharpening Review (006Z4, 2026-07-12)

- Consume the immutable `active_member_snapshot` persisted on the application's eligibility
  assessment, or a member result whose `result_id` exactly matches the member's verified active-status
  result. Require `calculated_as_of_date`, `member_active_check`, `qualification_route`, and the
  verified result identifier; never treat an unverified calculation or `manual_evidence_required`
  result as limit authority.
- The borrower projection may expose the result identifier/date and limit/advisory facts only. It
  must strip `member_id`, `verified_by_user_id`, evidence references, classified row IDs, and staff
  actions already retained in the internal snapshot.
