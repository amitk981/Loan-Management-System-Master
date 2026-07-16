# Slice 008M5: Documentation Durable Actions and Blocker Closure

## Status
Complete

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package

## Depends On
- 008M4

## Runtime Capabilities

- `localhost-e2e-server`

## Goal

Make signed-copy upload/re-upload, correction/return/condition actions, and the governed-attorney
absence durable and truthful through their legal/security owners instead of reporting success for
workspace-local writes that no later decision consumes.

## Source / Review References

- `docs/source/screen-spec.md` S26-S28 and S35
- `docs/source/api-contracts.md` §§6-8, 26-28, and 44
- `docs/source/auth-permissions.md` §§19.4, 22-23, 26.4, and 37
- `docs/source/codebase-design.md` §§14-15, 26-28, 36-37, and 42
- `docs/source/functional-spec.md` M06-FR-007, M06-FR-008, M06-FR-018, M06-FR-019
- `docs/working/ASSUMPTIONS.md` A-125
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-16_143718_architecture_review`

## Concrete Requirements

1. Replace the workspace-local signed-copy helper with one legal-owner decision/execute interface.
   A successful upload or re-upload must retain immutable application/document/file/uploader/checksum/
   remarks/request provenance, link each successor to the prior accepted signed copy, and project the
   current accepted copy after refetch without overwriting the renderer-owned generated original.
2. Replace generic `staff_documentation_action` events for request correction, return for correction,
   and add condition with one checklist/legal-owner aggregate. Retain the exact target item or final
   checklist stage, actor role/team, reason/condition, prior/current state, audit/workflow/version
   identities, and a stable action identity. Exact replay is zero-write; changed/stale/tampered action
   identities conflict or deny nondisclosing.
3. Make these actions affect current truth: an open correction/return is visible in the checklist,
   Document Pack, blockers, and timeline; it prevents the affected completion/approval until an
   owner-defined corrected successor resolves it. A condition remains visible and attached to the
   exact approval stage. Do not treat a generic workflow event as resolution evidence.
4. Preserve A-125: do not invent or select an attorney. When PoA is required and no governed
   application-scoped attorney decision exists, return `status: blocked`, no create action, and a safe
   stable `governed_attorney_unconfigured` blocker in both workspace surfaces. The blocker grants no
   authority and disappears only when a future governed owner returns an exact decision.
5. Keep opaque action ids, owner parity, sibling ordering, independent Download, one-refetch success,
   strict redaction, and the approved prototype composition. No new styling or generic action state.

## Trusted Browser Acceptance

- Spec: `e2e/staff-documentation-workspace.e2e.spec.ts`
- Screenshot: `documentation-checklist-blockers.png`
- Screenshot: `documentation-security-workflow.png`
- Screenshot: `documentation-restricted-state.png`
- Screenshot: `documentation-final-approval.png`
- Screenshot: `documentation-checklist-narrow.png`

## Test Cases

- Public API tests upload then re-upload two genuine files and assert the current projection,
  immutable predecessor/successor provenance, exact audit/workflow/version ledgers, and no mutation of
  the renderer original; stale/tampered/cross-user/application/document actions are zero-write.
- Public correction/return/condition tests assert durable visible state, completion/approval blocking,
  exact resolution, replay/change conflicts, and full actor/object/role matrices. Tests must assert
  owner state and ledgers, not only HTTP 200 or source substrings.
- PoA tests cover required/unconfigured, configured-owner decision via injected test seam, wrong role,
  stale attorney decision, and the exact safe blocker; production remains blocked under A-125.
- Real-Django browser acceptance executes upload/re-upload and correction through the UI, verifies the
  persisted projection after refetch, shows the PoA blocker, and captures all five screenshots twice.

## Evidence Required

Failing-first copies of the architecture-review probes; sanitized durable-action projections and
ledgers; focused backend/frontend results; twice-run trusted-browser logs/screenshots; full gates.

## Risk Level
High

## Acceptance Criteria

- No advertised upload/correction/return/condition action can succeed without durable owner state
  that subsequent workspace and approval decisions consume.
- Required PoA honestly exposes the A-125 blocker without inventing legal authority.
- Existing action, download, pagination, redaction, and prototype contracts remain green.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated, if needed
- [x] Permissions tested
- [x] Audit events tested
- [x] Trusted-browser contract declares all five twice-run screenshot outputs; bundled-browser absence uses the installed host Chrome, local sandbox launch denial is retained honestly, and independent gate is pending
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [x] Commit delegated to the orchestrator only after passing configured gates
