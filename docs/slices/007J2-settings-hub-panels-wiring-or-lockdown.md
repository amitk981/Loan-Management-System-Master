# Slice 007J2: SettingsHub Remaining Panels — Wiring or Lockdown

## Status
Not Started

## Parent Epic
Epic 007: Sanction Approval Workflow and Registers
Epic file: `docs/epics/007-sanction-approval-workflow.md`

## Goal
Resolve every SettingsHub panel that is not the approval matrix (007J owns that one): each panel is either wired to the real versioned configuration APIs or rendered explicitly read-only/disabled with a recorded non-MVP treatment. Today the hub shows editable-looking inline policy/rate/threshold/retention data with no backend (PRODUCTION_COMPLETION_BLUEPRINT.md §6.3).

## User Value
Admins cannot believe they changed a production policy when nothing was saved; every live setting shown is backend truth.

## Depends On
- 007J

## Source References
- docs/source/screen-spec.md S71 settings area
- docs/source/functional-spec.md configuration requirements per module
- docs/slices/003E-versioned-configuration-shell.md (versioned config pattern)
- docs/slices/006C-loan-limit-configuration-and-calculator.md (loan limit config contract)
- docs/working/ASSUMPTIONS.md

## Prototype Reference
- sfpcl-lms/src/pages/settings/SettingsHub.tsx

## Concrete Requirements
1. Inventory every panel/control in `SettingsHub.tsx`. For each, classify: (a) backed by an existing source-backed config API (003E shell, 006C loan-limit config, 003F templates, 007A matrix — already owned by 007J); (b) source-required but no backend yet; (c) not source-required.
2. Class (a): wire the panel to its API — display current version, edits only for permitted roles, every edit creates a new config version (003E pattern), audit event, stale-write handling.
3. Class (b): render read-only with an explicit "configuration managed outside the product until slice X" note; create or name the owning future slice in the review packet; record in ASSUMPTIONS.md.
4. Class (c): remove the control; note the removal in the review packet.
5. No inline default values presented as live policy anywhere in the hub afterward.
6. Loading/error/unauthorized/read-only states throughout; existing patterns only.

## Owned Mock Removals
- `src/pages/settings/SettingsHub.tsx` — no inline policy/rate/threshold/retention fixtures presented as live data.

## Test Cases
- Each wired panel round-trips a version-creating edit with audit; non-permitted role is read-only and 403 on direct call.
- Read-only panels expose no mutation path.
- Regression: no inline config fixture rendered as editable/live.

## Run-Ahead Sharpening Review (007I delivered frontend authority pattern, 2026-07-13)

- Follow 007I's fail-closed authority rule for every versioned settings resource: an `/auth/me`
  permission may make a resource action usable, but must never create a missing resource action or
  turn a disabled action into an enabled control.
- Keep SettingsHub independent from approval-case and register reads. The approval workbench's
  frozen `matrix_projection` is historical display truth for one cycle, not the current editable
  configuration source and never a fallback when the settings endpoint is denied or empty.
- Add a raw-source regression that rejects editable-looking inline policy/rate/threshold/retention
  fixtures after classification, while allowing explicit controlled vocabularies and inert labels.

## Out of Scope
Approval matrix panel (007J), new configuration domains not in the source, notification/communication template content (003F).

## Risk Level
Medium

## Acceptance Criteria
- Every SettingsHub surface is either real and versioned or explicitly inert with a recorded owner.
- All gates pass; screenshots of each panel's final state saved.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Visual evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit created only after passing gates
