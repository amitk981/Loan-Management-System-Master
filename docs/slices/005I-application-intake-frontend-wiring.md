# Slice 005I: Application Intake Frontend Wiring (List, New, Detail)

## Status
Complete

## Parent Epic
Epic 005: Loan Application Intake, Documents, Completeness, and Deficiencies
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal
Wire the core staff application screens to the backend APIs built in 005A-005F: Application List, New Loan Application (S10), Application Draft Review / Detail (S11), including document checklist and deficiency status display. The Completeness Workbench was wired in 005E; this slice closes the rest of the intake surface.

## User Value
Staff create, review, and track real loan applications in the screens they already use — the single most-used workflow in the system stops running on mock data.

## Depends On
- 005H

## Prior Slice Facts To Preserve
- 005G2 closed portal session/audit contract hardening. Staff screens must remain on staff
  audit/action semantics; do not consume portal audit action names or portal own-data permissions
  for staff intake flows. If a browser has an old suspended portal session, `/auth/me` now returns
  `401 INVALID_TOKEN` and must clear local session state through the existing auth-session path.
- 005G portal application endpoints are borrower own-data APIs only; staff screens must use the
  existing staff `/api/v1/loan-applications/` APIs and staff object-access rules, not portal routes.
- Submitted applications may have no `LO...` reference until completeness pass generates it.
- Returned applications must display `application_status = incomplete_returned`,
  `completeness_status = incomplete`, and `current_stage = initial_loan_request` without treating
  them as plain submitted applications.
- Do not reintroduce `mockData.ts` application rows into Application List, New Application, or
  Application Detail once a screen is wired to backend data.
- If staff UI surfaces audit/status history, distinguish internal staff application events from
  borrower portal events. Portal actions such as `portal.application.submitted` are evidence that a
  borrower acted through the portal, not a replacement for staff-side application audit actions.
- 005H adds staff-only rejection-note metadata endpoints:
  `POST /api/v1/loan-applications/{loan_application_id}/rejection-note/` and
  `POST /api/v1/rejection-notes/{rejection_note_id}/send/`. Rejection notes serialize
  `rejection_note_id`, `loan_application_id`, `rejection_stage`, `rejection_reason_category`,
  `detailed_reason`, `reapply_allowed_flag`, `note_status = draft/sent`, prepared/sent actor IDs,
  timestamps, `communication_mode`, and nullable `communication_id`.
- Rejection-note create/send are staff-only and currently require
  `applications.loan_application.complete_check`. Active borrower portal sessions receive
  `403 PERMISSION_DENIED`; old suspended portal sessions receive `401 INVALID_TOKEN` through the
  shared auth path. Staff UI must not route rejection-note controls through portal APIs.
- Rejection-note creation does not change `application_status` in 005H. Staff detail UI should show
  rejection-note status as separate metadata when available, while keeping the application status
  returned by the detail API. Do not invent a frontend-only rejected state.
- Rejection-note send is metadata-only in 005H: no PDF, no communication row, no provider delivery,
  and no borrower portal delivery surface exists yet.

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
3. Wire `ApplicationDetail.tsx` to the detail API: stage stepper from real status, document
   checklist state, deficiency list and resolution status (005F), and rejection note state (005H)
   if a staff action/status slot already exists. Preserve existing cards, badges, tables, and
   action-panel patterns; do not introduce new styling for rejection notes.
4. Loan Request Register view (S13) renders from the register API (005C) inside the existing list patterns.
5. Loading, empty, validation-error, unauthorized, and success states throughout.
6. Preserve portal/staff separation: MP05/MP09/MP10 remain on portal APIs; staff intake screens
   remain on staff APIs and must surface `403 OBJECT_ACCESS_DENIED` distinctly from missing
   permissions where the backend returns it.

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
