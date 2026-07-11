# Slice 006H5: App Shell Application State Authority

## Status
Not Started

## Parent Epic
Epic 006: Eligibility, Loan Limit, Appraisal, and Credit Review
Epic file: `docs/epics/006-eligibility-loan-limit-appraisal.md`

## Goal
Stop the app shell from seeding production workflow state with mock data. `App.tsx` currently imports `loanApplications as initialApplications` from `mockData.ts` and passes that state into screens (including SanctionWorkbench), which makes mock records look like real workflow state (PRODUCTION_COMPLETION_BLUEPRINT.md §6.3).

## User Value
No staff user can mistake a mock application for a real one anywhere in the shell; screens that are not yet API-wired show an explicit not-wired/empty state instead of plausible fake data.

## Depends On
- 006H4

## Source References
- docs/working/FRONTEND_DESIGN_RULES.md (no new mock data; wire to real APIs)
- docs/working/PRODUCTION_COMPLETION_BLUEPRINT.md §6.3 (App shell application state row) and §6.4 (mock ratchet)
- docs/working/PROTOTYPE_GAP_REPORT.md Major Conflict Policy

## Prototype Reference
- sfpcl-lms/src/App.tsx
- sfpcl-lms/src/pages/sanction/SanctionWorkbench.tsx (consumer; its own wiring is 007I)

## Concrete Requirements
1. Remove the `mockData` import from `src/App.tsx`. Application workflow state must not be seeded client-side.
2. Screens already wired to backend APIs are unaffected; audit each consumer of the removed prop chain. Any screen that still needed the mock state (SanctionWorkbench until 007I runs) renders an explicit empty/not-wired state using existing empty-state patterns — never a mock fallback that looks like real data.
3. Do not wire SanctionWorkbench to sanction APIs in this slice; that is 007I. This slice only removes the mock authority and makes the gap visible and honest.
4. No visual redesign; reuse existing empty/loading/error patterns.

## Owned Mock Removals
- `src/App.tsx` — no `mockData` import remains.

## Test Cases
- Regression: `src/App.tsx` does not import `src/data/mockData.ts`.
- SanctionWorkbench (and any other consumer) renders its explicit empty/not-wired state without runtime errors.
- Existing wired screens' suites remain green; build/typecheck/lint pass.

## Out of Scope
SanctionWorkbench API wiring (007I), registers (007J), header search/notifications (010N/010O).

## Risk Level
Medium

## Acceptance Criteria
- The total mock/fixture surface shrinks by the App.tsx path and no production screen gains a mock fallback.
- Screenshots of each affected consumer's empty/not-wired state saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates

## Run-Ahead Sharpening Review (005FA3, 2026-07-11)

- The owned removal is exactly `App.tsx`'s `mockData` application seed and local update chain.
  Audit every prop consumer, but do not absorb 007I sanction API wiring.
- Mount each affected consumer with an empty authoritative input and assert the existing explicit
  empty/not-wired composition; also assert no replacement inline fixture or new mock import.
