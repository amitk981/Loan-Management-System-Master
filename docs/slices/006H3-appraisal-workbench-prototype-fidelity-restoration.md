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
- 006H7

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
- Keep 006H2/006H4 writable projections, authoritative resource `available_actions`, case reload,
  real-container behavior tests, errors, and exact
  action bodies. Do not restore mock calculations, invented statuses, local exception decisions,
  JSON downloads, console audit, or mock member/application facts.
- Use only existing components/classes and compositions. Any prototype control whose backend
  behavior belongs to a later epic remains hidden/disabled with an existing pattern, not replaced
  by a new layout.

## Test Cases

- Behavior tests from 006H2 and the real-container interaction suite from 006H4 remain unchanged
  and green through the restored composition.
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
- Restored controls must continue to require the matching resource action code plus current-user
  permission/role usability; global permissions must never be unioned into resource actions, and
  legacy revalidation remains distinct from submit-for-review.
- Preserve 006H6's full six-field `AvailableAction` objects and real-container HTTP tests unchanged;
  the fidelity restoration may move controls within the approved prototype composition, but it may
  not flatten actions to strings, hide disabled reasons, reintroduce local state gates, or replace
  the canonical four-way post-mutation reload with optimistic status synthesis.

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

## Run-Ahead Sharpening Review (006H5, 2026-07-11)

- Visual restoration must preserve the shell's zero mock application authority: do not re-add an
  `App.tsx` application collection, status updater, or `mockData` import while composing the
  appraisal stages.
- The focused Playwright matrix remains appraisal-only. Sanction queue screenshots and API wiring
  belong to 007I; this slice may show only the canonical sanction-case readback already required
  by 006H6.

## Run-Ahead Sharpening Review (006G5, 2026-07-11)

- Reconfirmed that this is presentation restoration only: preserve 006H6's public module action
  seams, full action objects, exact four-read refresh, and the canonical credit/approvals dependency
  direction while moving controls back into the approved prototype composition.
- The declared Playwright state matrix and self-contained screenshots are acceptance evidence, not
  optional local feedback; no sanction queue wiring or mock application state belongs here.

## Run-Ahead Sharpening Review (006H6, 2026-07-11)

- Preserve module-owned eligibility, loan-limit, and appraisal action projections; presentation
  restoration must not recreate `_credit_action_snapshot` or any response-key action heuristic.
- The current container awaits one canonical four-read reload after every successful mutation and
  retains disabled six-field actions for their reasons. Visual movement must preserve both facts
  and must keep response-only `available_actions` out of frozen appraisal/audit snapshots.

## Run-Ahead Sharpening Review (architecture review 2026-07-11_212738)

- 006H7 now owns the missing mounted-container interaction matrix and exact public-service action
  parity. This fidelity slice must keep that suite unchanged and green; server-rendered child tests
  or source-text assertions are not substitutes if controls move within the restored composition.
- The restored UI must display backend disabled reasons without inferring maker-checker, reference,
  eligibility, provenance, history, state, role, or object-scope rules in React.
