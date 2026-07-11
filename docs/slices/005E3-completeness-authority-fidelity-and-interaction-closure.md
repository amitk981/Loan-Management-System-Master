# Slice 005E3: Completeness Authority, Fidelity, and Interaction Closure

## Status
Not Started

## Parent Epic
Epic 005: Application Intake and Completeness
Epic file: `docs/epics/005-application-intake-completeness.md`

## Goal

Close 005E2's remaining authority and acceptance gaps: make both completeness reads meaningful,
project resource actions from backend gates, restore the approved S12 composition, and prove every
workbench mutation through the real container.

## Depends On
- 005E2

## Runtime Capabilities
- `localhost-e2e-server`

## Source / Review References
- `docs/source/screen-spec.md` S12-S14
- `docs/source/api-contracts.md` §19.6-§21.3 and §44
- `docs/source/auth-permissions.md` §23 and §34.3
- `docs/source/codebase-design.md` §23.3-§23.5 and §26.3
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-11_191720_architecture_review`

## Scope

- Make `GET .../document-checklist/` authoritative for document submission/verification rows and
  `GET .../completeness-check/` authoritative for application, nominee, blocker, reference, and
  workflow facts. Join by document type and fail closed with an existing error pattern if the two
  projections disagree; do not keep a discarded/decorative request.
- Add full §44-shaped `available_actions` to the completeness/deficiency read boundary behind an
  applications-module seam. Enabled/disabled results must reuse the exact pass, return, resolve,
  and rejection-note permission/object/state validators; the HTTP view and React page must not own
  a second action matrix.
- React preserves full action objects, intersects them with `/auth/me` only for usability, shows
  backend disabled reasons where useful, and exposes no mutation when an action is absent. Remove
  the single global `complete_check` switch as authority for every action.
- Restore the pre-005E2 S12 category grouping, item/detail/document-chip composition, card
  hierarchy, density, and action placement. Change only data, labels, visibility, and handlers;
  never restore mock facts, local checklist decisions, local reference generation, or local
  workflow outcomes.
- After pass, return, resolve, and reject, reload canonical queue/detail/checklist/history state.
  A `409` performs one mutation request, no automatic retry, and a canonical refresh only when the
  user chooses it.

## Test Cases

- Backend action/service parity matrix covers allowed and denied permission, object, application
  state, blocker, open-deficiency, duplicate-note, and reference/register cases.
- Mount the default `CompletenessWorkbench` with mocked HTTP; exercise pass, return, resolve, and
  reject and assert exact URL/body/count, canonical reads, visible refreshed state, field errors,
  `401`/`403`, and one-call `409` behavior.
- Prove a globally permissioned actor sees no control when the resource action is absent/disabled,
  and direct backend calls remain denied without writes.
- Prove both checklist projections affect rendering and a mismatch fails closed. Preserve complete
  open/resolved deficiency history and backend-issued reference display.
- Run the pinned Playwright path and capture queue/detail, pass, returned, resolved, rejected,
  denied, stale, and API-error screenshots against the restored prototype composition.

## Evidence Required

Failing-first action/checklist/container output, backend action parity matrix, exact HTTP examples,
prototype-fidelity checklist, deterministic Playwright screenshots, and all configured gates.

## Risk Level
High

## Acceptance Criteria

- No discarded completeness request and no frontend-owned action/workflow matrix remains.
- Every mutation is proven through the real container and backend gate, including denial and stale
  paths.
- The real-data screen is visually indistinguishable from the approved pre-005E2 S12 composition.

