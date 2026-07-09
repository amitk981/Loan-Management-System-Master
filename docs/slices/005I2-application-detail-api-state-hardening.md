# Slice 005I2: Application Detail API State Hardening

## Status
Complete

## Parent Epic
Epic 005: Loan Application Intake, Documents, Completeness, and Deficiencies
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal
Close the architecture-review finding from `2026-07-10_041851_architecture_review`: the staff
Application Detail screen must not use hardcoded mock-loan state after 005I made the intake surface
API-backed.

## User Value
Staff see the backend-owned application status, document state, rejection-note state, and related
detail facts for every real application, without stale prototype special cases overriding live data.

## Depends On
- 005I

## Source / Review References
- `docs/slices/005I-application-intake-frontend-wiring.md` requires Application Detail to show real
  detail API state, document checklist state, deficiencies, and 005H rejection-note state where an
  existing detail slot can support it.
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-10_041851_architecture_review`.
- `docs/working/digests/epic-005-application-intake.md` 005H and 005I extracts.
- `docs/working/API_CONTRACTS.md` loan-application and rejection-note sections.

## Prototype Reference
- `sfpcl-lms/src/pages/applications/ApplicationDetail.tsx`
- Existing `StatusBadge`, `AlertBanner`, `StageStepper`, `DocumentChecklist`, and action-panel
  patterns already used on Application Detail.

## Frontend Scope
- Remove all `LO00000035` special-case logic and any hardcoded status/owner/document overrides from
  Application Detail. Stage, owner, document badge, and status label must derive from backend API
  fields or display neutral unavailable state.
- Remove hardcoded witness rows and hardcoded nominee sensitive values from Application Detail. If a
  backend field is not available yet, show an empty/unavailable state using existing patterns rather
  than synthetic person data.
- Add a render regression test that feeds an API-backed application with `application_reference_number
  = LO00000035` and proves the screen does not force `Sanctioned · Documentation Pending`,
  `11 items pending`, or fake witness names.
- Preserve current styling exactly; change only data wiring, labels, visibility, and role/action
  logic.

## Backend/API Scope
- Add optional rejection-note summary to the existing staff application detail response if a
  `RejectionNote` exists for the application. Do not create a broad new endpoint unless the existing
  serializer cannot expose the needed read fact cleanly.
- The detail response should include only metadata-safe rejection-note fields already serialized by
  005H: `rejection_note_id`, `note_status`, `rejection_stage`, `rejection_reason_category`,
  `reapply_allowed_flag`, prepared/sent actor IDs, timestamps, `communication_mode`, and nullable
  `communication_id`.
- Do not add create/send UI controls unless an existing action slot can express them without new
  styling and the backend permission is already available. Showing status/read metadata is the
  corrective requirement.

## API Contracts
- Update `docs/working/API_CONTRACTS.md` to state that staff application detail may include nullable
  `rejection_note` metadata and that `application_status` remains backend-owned.

## Permissions
- Preserve existing staff application read/object-access ordering: missing global read permission
  returns `403 PERMISSION_DENIED`; same-permission out-of-scope staff receive
  `403 OBJECT_ACCESS_DENIED`; unknown application IDs return `404 NOT_FOUND`.
- Do not expose staff rejection-note metadata through borrower portal application routes.

## Audit Requirements
- Read-only detail/rejection-note summary access writes no success audit or workflow event.

## Validation Rules
- Application Detail must not synthesize status, owner, document blockers, witnesses, nominee
  identifiers, or rejection state from frontend-only constants.
- If backend facts are absent, render an empty/unavailable state with existing visual patterns.
- Sensitive nominee/member identifiers must remain masked-only unless a future backend reveal API
  authorizes and audits reveal.

## Test Cases
- Backend detail response includes `rejection_note` when one exists and `null` when absent.
- Backend object-access denial still hides the detail and rejection-note metadata.
- Frontend Application Detail render test for API-backed `LO00000035` proves no mock override text or
  fake witness rows appear.
- Frontend detail test shows rejection-note status metadata when the API returns it.
- Existing Application List/New Application tests continue to pass.

## Visual Acceptance Criteria
Use the existing Application Detail cards, badges, tabs, and alert/empty patterns. Save visual
evidence for a detail page with no witness/rejection-note facts and a detail page with a rejection
note summary.

## Evidence Required
Backend red/green logs, frontend red/green logs for Application Detail regression tests, standard
quality-gate logs, and visual evidence.

## Risk Level
Medium

## Acceptance Criteria
- Application Detail derives displayed state from staff APIs and no longer contains the `LO00000035`
  mock special case or hardcoded witness/sensitive nominee values.
- Staff detail can display existing rejection-note metadata separately from application status.
- Permissions, object access, no-audit read behavior, and frontend rendering are tested.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated, if needed
- [x] Permissions tested
- [x] Visual evidence saved
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [ ] Commit created only after passing gates
