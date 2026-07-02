# Slice 005I: Application Intake Frontend Wiring (List, New, Detail)

## Status
Not Started

## Parent Epic
Epic 005: Loan Application Intake, Documents, Completeness, and Deficiencies
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal
Wire the core staff application screens to the backend APIs built in 005A-005F: Application List, New Loan Application (S10), Application Draft Review / Detail (S11), including document checklist and deficiency status display. The Completeness Workbench was wired in 005E; this slice closes the rest of the intake surface.

## User Value
Staff create, review, and track real loan applications in the screens they already use — the single most-used workflow in the system stops running on mock data.

## Depends On
- 005H

## Source References
- docs/source/screen-spec.md screens S10 (New Loan Application), S11 (Application Draft Review), S13 (Loan Request Register)
- docs/source/api-contracts.md section 19 (loan application APIs), 20 (application document APIs), 21 (deficiency/rejection APIs)
- docs/source/user-flows.md (application intake flows)
- docs/source/content-spec.md (form labels and stage wording)

## Prototype Reference
- sfpcl-lms/src/pages/applications/ApplicationList.tsx
- sfpcl-lms/src/pages/applications/NewApplication.tsx
- sfpcl-lms/src/pages/applications/ApplicationDetail.tsx

## Concrete Requirements
1. Wire `ApplicationList.tsx` to the list API with real pagination, filtering, and sorting per api-contracts §8 (page_size default 20, max 100) — no client-side-only filtering of mock arrays.
2. Wire `NewApplication.tsx` to draft create/update/submit APIs (005A/005B) with member lookup, reference number display (005C), and required-document placeholders (005D); preserve the multi-step form structure per FRONTEND_DESIGN_RULES.
3. Wire `ApplicationDetail.tsx` to the detail API: stage stepper from real status, document checklist state, deficiency list and resolution status (005F), rejection note state (005H).
4. Loan Request Register view (S13) renders from the register API (005C) inside the existing list patterns.
5. Loading, empty, validation-error, unauthorized, and success states throughout.

## Test Cases
- List pagination/filter/sort round-trips against seeded data.
- Draft save → submit → detail reflects backend status transitions; invalid submit shows field errors from the error envelope.
- Unauthorized role cannot see create action (frontend) and gets 403 (backend, already tested in 005A-B — assert wiring surfaces it).

## Out of Scope
Completeness workbench (005E done), member portal application screens (005G), appraisal actions (006H).

## Risk Level
Medium

## Acceptance Criteria
- The application intake surface runs fully on backend data; no `mockData.ts` reads remain in these screens.
- Visual structure matches the prototype (visual-regression baselines updated only if 002EY harness flags intentional data-driven diffs).
- All gates pass; screenshots of list, new-application steps, and detail saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Permissions tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
