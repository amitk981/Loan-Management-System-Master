# Slice 005E2: Completeness Workbench Real-Data Corrective

## Status
Complete

## Parent Epic
Epic 005: Application Intake and Completeness
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal
Remove every mock read and client-side business decision from `CompletenessWorkbench.tsx` and wire it to the existing Epic 005 backend APIs. 005I recorded 005E as already wired; the production completion audit (PRODUCTION_COMPLETION_BLUEPRINT.md §6.3) confirmed the screen still runs entirely on mock data.

## User Value
The Credit Assessment Team performs the real completeness gate on real applications; a completeness pass, deficiency, return, or rejection recorded in the UI is the backend truth, not a local simulation.

## Depends On
- 005I

## Source References
- docs/source/screen-spec.md completeness screens (S12-S14 range)
- docs/source/api-contracts.md sections 20-22 (checklist, completeness, deficiency APIs)
- docs/source/functional-spec.md M03 completeness requirements
- docs/working/PRODUCTION_COMPLETION_BLUEPRINT.md §6.3 (Completeness Workbench row)

## Prototype Reference
- sfpcl-lms/src/pages/applications/CompletenessWorkbench.tsx
- sfpcl-lms/src/pages/applications/completenessChecklist.ts

## Concrete Requirements
1. Remove the `documents, loanApplications, members` imports from `src/data/mockData.ts`, the hard-coded `seededDeficiencies` map, and the local `getInitialChecks` derivation. Checklist state comes from `GET /api/v1/loan-applications/{id}/document-checklist/` and `.../completeness-check/` (both already routed in `sfpcl_credit/config/urls.py`).
2. The queue lists real applications from the application list API filtered to submitted/returned-for-rectification statuses; no mock queue rows remain.
3. Remove client-side loan-reference generation (`getNextLoanReference`). Reference numbers are display-only values returned by the backend (005C owns generation); the completeness pass action calls `POST .../completeness-check/pass/` and re-renders the backend response.
4. Deficiency creation/resolution and return/reject actions call the 005F/005F2/005H APIs with exact request bodies; comments/reasons required by those contracts are enforced by the backend, surfaced as field errors.
5. Action visibility follows the resource `available_actions` authority pattern established by 006H4 where the API provides it; otherwise permission-gate with `/auth/me` codes and record the interim in API_CONTRACTS.md.
6. Loading, empty, error, unauthorized, validation, and stale (409) states throughout; reuse existing patterns only, no new visual design.

## Owned Mock Removals
- `src/pages/applications/CompletenessWorkbench.tsx` — no `mockData` import or inline business fixtures remain.

## Test Cases
- Regression: the wired workbench path does not import `src/data/mockData.ts`.
- Queue rows come from the API; each action asserts exact URL/body and re-renders backend state.
- Completeness pass shows the backend-issued reference; no reference is computed client-side.
- Non-permitted role sees no actions and direct API calls return 403.

## Sharpened Source Anchors (2026-07-11 Architecture Review)

- M03-FR-010 and S12 assign completeness review to Deputy Manager – Finance; Credit Manager may
  participate only through the already-seeded backend permission/object boundary. The frontend
  must not infer ownership from application creator/receiver fields.
- The canonical pass endpoint is the implemented
  `POST /api/v1/loan-applications/{id}/completeness-check/pass/`, not the source example's older
  generic `complete-check` shape. It must surface the backend's nine required document blockers
  and delegate reference generation to the existing 005C transaction.
- Returned rows are `application_status = incomplete_returned`, `completeness_status = incomplete`,
  with no reference/register/sequence advancement. Repeat staff return remains a backend `409`
  until the borrower resubmission slice supplies a source-backed transition.
- Preserve complete deficiency history. The UI may display current open rows and resolved rows but
  must not overwrite or collapse earlier deficiency cycles into one local map.

## Out of Scope
Member portal deficiency response (008L2), rejection-note content changes (005H), checklist rule changes (005D).

## Risk Level
Medium

## Acceptance Criteria
- Completeness decisions recorded in the UI exist as backend state with audit events.
- No mock reads or client-side completeness/reference/deficiency decisions remain in the screen.
- All gates pass; screenshots of queue, detail, pass, deficiency, and returned states saved.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated, if needed
- [x] Permissions tested
- [x] Audit events tested
- [x] Visual evidence saved
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates
