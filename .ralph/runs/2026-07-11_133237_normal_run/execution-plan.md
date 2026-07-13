# Execution Plan

Selected slice: `006H4-workbench-authoritative-actions-and-container-tests`

## Boundaries and authority

- Change only Epic 006 appraisal/eligibility/loan-limit/sanction read projections, the existing
  Appraisal Workbench container, their tests, API-contract documentation, and Ralph artifacts.
- Keep the approved frontend composition unchanged; 006H3 owns visual fidelity restoration.
- Treat each selected resource's backend `available_actions` as authoritative. `/auth/me` roles and
  permissions may only narrow usability and must never add an action absent from the resource.
- Preserve the sanction case's stored `workflow_event_id` verbatim on submit and reload.

## TDD tracer bullets

1. Add one backend API assertion for the standard available-action projection and capture RED;
   implement the smallest object/state-aware projection for that endpoint and capture GREEN.
2. Repeat vertically across eligibility run, loan-limit calculate, appraisal create/update,
   legacy revalidation, submit-review, review/return/reject, and sanction submit/read states.
3. Replace the static-only workbench test gap with a real default-container mocked-HTTP interaction
   test proving a globally permissioned user gets no control when the resource action is absent;
   capture RED, then remove the global/resource union and capture GREEN.
4. Add container interactions one behavior at a time for Deputy Manager Finance, Credit Manager,
   zero permission, disabled/missing actions, object denial, returned draft, legacy revalidation,
   conditional rejection, stale 409, and sanction reload. Assert exact URL/body, request count,
   visible outcome, canonical IDs/status, and writable PATCH allowlists.

## Verification and close-out

- Run focused backend and frontend tests after each tracer bullet, then backend Django check,
  migration sync, full coverage suite, and frontend build/typecheck/lint/full Vitest gates.
- Save red/green logs and exact HTTP examples under the run evidence directory.
- Review the diff for protected paths, scope, mock-surface regression, action-authority precedence,
  response-only PATCH leakage, and configured diff limits.
- Update API contracts if the response projection changed; write changed-files, risk assessment,
  review packet, final summary, progress/state/handoff, mark 006H4 Complete, and sharpen the next
  one or two Not Started slices only from already-opened Epic 006 material.
