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
- Visual regression covers queue, eligible/ineligible/pending, below/equal/above limit, draft,
  returned, review-pending, reviewed, rejected, submitted, empty, loading, denied, validation, and
  API-error states at the existing acceptance viewport.
- Static diff/fidelity review proves no new color, typography, card, badge, table, or layout pattern.

## Evidence Required

Before/after host screenshots, visual-regression output, prototype-fidelity checklist, and all
configured gates. A missing browser/listener is failure for this corrective slice, not a deferral.

## Risk Level
Medium

## Acceptance Criteria

- The real API-backed workbench is visually indistinguishable from the approved prototype language.
- No business rule or mock credit fact returns to React.
