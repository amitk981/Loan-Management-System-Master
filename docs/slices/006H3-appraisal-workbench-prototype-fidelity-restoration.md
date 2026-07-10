# Slice 006H3: Appraisal Workbench Prototype Fidelity Restoration

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal

Restore the approved staged Appraisal Workbench, eligibility checklist, and calculator composition
while retaining the corrected 006H2 backend wiring and introducing no new visual design.

## Depends On
- 006H2

## Source / Review References
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/working/VISUAL_ACCEPTANCE.md`
- Prototype versions of `AppraisalWorkbench.tsx`, `EligibilityChecklist.tsx`, and
  `LoanLimitCalculator.tsx` immediately before 006H
- `docs/slices/006H-eligibility-appraisal-frontend-integration.md`
- `docs/working/REVIEW_FINDINGS.md` entry for this review

## Scope

- Restore the approved queue/detail/staged-workflow structure, card hierarchy, density, spacing,
  badges, and disclosure patterns from the pre-006H prototype. Replace only labels, API data,
  visibility, and action handlers needed for real Epic 006 facts.
- Keep 006H2 writable projections, server `available_actions`, case reload, errors, and exact
  action bodies. Do not restore mock calculations, invented statuses, local exception decisions,
  JSON downloads, console audit, or mock member/application facts.
- Use only existing components/classes and compositions. Any prototype control whose backend
  behavior belongs to a later epic remains hidden/disabled with an existing pattern, not replaced
  by a new layout.

## Test Cases

- Behavior tests from 006H2 remain unchanged and green through the restored composition.
- Add a focused spec under `sfpcl-lms/e2e/` that uses the repository-pinned `@playwright/test`
  Chromium project. Visual regression covers queue, eligible/ineligible/pending,
  below/equal/above limit, draft, returned, review-pending, reviewed, rejected, submitted, empty,
  loading, denied, validation, and API-error states at the existing acceptance viewport.
- Static diff/fidelity review proves no new color, typography, card, badge, table, or layout pattern.

## Sharpened Carry-Forward Contract

- Preserve `projectAppraisalDraft` as the only response-to-edit/PATCH seam and keep its exact ten
  top-level writable keys plus the five nested risk keys covered by 006H2.
- Preserve the four-way reload (`eligibility`, `loan-limit`, `appraisal`, `sanction-case`) and treat
  sanction-case `404 NOT_FOUND` as absence while displaying the exact returned case UUID and
  application/appraisal statuses.
- Restored controls must continue to require the matching server action code plus current-user
  permission/role usability; legacy revalidation remains distinct from submit-for-review.

## Evidence Required

Before/after host screenshots, Playwright visual-regression output, prototype-fidelity checklist,
and all configured gates. The authoritative capture path is the repository's pinned
`sfpcl-lms/e2e/` Playwright harness with `E2E_DJANGO_PYTHON` set to the Ralph virtualenv. It must
be an absolute path because Playwright starts Django from the repository root. The harness must
write self-contained screenshots into the run evidence directory and commit the approved visual
baseline beside the focused e2e spec.

The in-app Browser may be used for exploratory inspection, but its listener is not a prerequisite
and must not replace or block the deterministic repository harness. Failure to launch the pinned
Playwright Chromium project or produce its screenshots is failure, not a deferral.

## Risk Level
Medium

## Acceptance Criteria

- The real API-backed workbench is visually indistinguishable from the approved prototype language.
- No business rule or mock credit fact returns to React.
