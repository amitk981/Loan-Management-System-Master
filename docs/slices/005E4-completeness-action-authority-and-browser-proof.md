# Slice 005E4: Completeness Action Authority and Browser Proof

## Status
Not Started

## Parent Epic
Epic 005: Application Intake and Completeness
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal

Finish 005E3 by enforcing each completeness mutation's source-defined permission behind one
applications-module action seam and by producing portable trusted-browser proof for every promised
workbench state.

## Depends On
- 005E3

## Runtime Capabilities
- `localhost-e2e-server`

## Trusted Browser Acceptance
- Spec: `e2e/completeness-workbench.e2e.spec.ts`
- Screenshot: `queue-detail.png`
- Screenshot: `pass.png`
- Screenshot: `deficiency.png`
- Screenshot: `returned.png`
- Screenshot: `resolved.png`
- Screenshot: `rejected.png`
- Screenshot: `denied.png`
- Screenshot: `stale.png`
- Screenshot: `api-error.png`

## Source / Review References
- `docs/source/auth-permissions.md` §12.4, §25.2, and §34.3
- `docs/source/api-contracts.md` §19.6-§21.3 and §44
- `docs/source/screen-spec.md` S12-S14
- `docs/source/codebase-design.md` §23.3-§23.5 and §26.3
- `docs/slices/005E3-completeness-authority-fidelity-and-interaction-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-11_212738_architecture_review`

## Scope

- Replace the shared completeness-check authority shortcut with the exact source permissions:
  `applications.loan_application.complete_check` for pass,
  `applications.loan_application.return_deficiency` for return,
  `applications.deficiency.resolve` for resolution, and
  `applications.rejection_note.create` for rejection-note creation. Each endpoint and its projected
  action must use the same permission, object-scope, state, and resource predicate.
- Return the full six-field §44 action shape (`action_code`, `label`, `enabled`, `disabled_reason`,
  `required_permission`, `required_role`) from the owning applications-module seam. Prove that an
  actor granted one action cannot see or invoke the other three and that denial writes no state,
  audit, workflow, register, deficiency, or rejection-note evidence.
- Keep 005E3's two-projection checklist join, full deficiency history, restored S12 composition,
  canonical post-mutation reload, and one-call 409 behavior unchanged.
- Make the Playwright spec derive every output from `RALPH_EVIDENCE_DIR`; remove the hard-coded run
  path. Add real denied and API-error states and capture all nine declared screenshots through the
  default routed container. Do not claim collection-only or unrelated tracer runs as acceptance.

## Test Cases

- Backend permission/object/state matrix exercises each of the four actions independently,
  including permission-only actors, wrong scope, wrong state, missing blocker/open deficiency,
  duplicate note/reference/register, exact error code, and zero-write denial.
- Module parity tests compare every projected enabled/disabled result and required permission/role
  with the corresponding public write boundary.
- The trusted Playwright run clicks pass, return, resolve, and reject, asserts exact URL/body/count
  and canonical reload, proves one-call 409/no retry, and renders denied and API-error states.
- Existing checklist mismatch, history, reference, frontend gate, and prototype-fidelity tests stay
  green without new styling or client-owned workflow decisions.

## Evidence Required

Failing-first permission/parity output, green backend matrix, exact HTTP examples, two successful
trusted-browser runs, all nine screenshots, prototype-fidelity checklist, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- No completeness action is projected or enforced through another action's permission.
- The portable browser contract executes every promised interaction/state and produces every
  declared screenshot in the current run evidence directory.
