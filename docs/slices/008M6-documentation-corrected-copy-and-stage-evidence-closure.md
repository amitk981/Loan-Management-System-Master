# Slice 008M6: Documentation Corrected-Copy and Stage-Evidence Closure

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package

## Depends On
- 008M5

## Runtime Capabilities

- `localhost-e2e-server`

## Goal

Make a staff signed-copy successor resolve a correction only while its exact file and immutable
owner ledgers remain coherent, and bind returns/conditions to the approval stage that actually
authorised the action.

## Source / Review References

- `docs/source/screen-spec.md` S26-S27 and S35
- `docs/source/api-contracts.md` §§6-8, 26-28, and 44
- `docs/source/auth-permissions.md` §§19.4, 23, 26.4, and 37
- `docs/source/codebase-design.md` §§14, 26-28, 36-37, and 42
- `docs/source/functional-spec.md` M06-FR-018 and M06-FR-019
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-16_213746_architecture_review`

## Concrete Requirements

1. Add one legal-owner current signed-copy reconciliation decision. A current successor must be the
   sole tail of the exact same-application/document predecessor chain and must match its retained
   `DocumentFile` id/checksum, uploader, remarks, request/action identity, resolution target, and
   singular audit/workflow/version bodies. Missing, duplicate, changed, cross-document, or stale
   evidence is not a current corrected copy.
2. `has_open_blocker`, workspace detail/queue, checklist completion, ordered approval, and later
   readiness must consume that decision. Merely having a reverse `resolved_by_signed_copy` relation
   must never clear a correction; changed file or ledger evidence restores the safe blocker without
   deleting history or mutating the renderer original.
3. Bind `request_correction`, `return_for_correction`, and `add_condition` commands to the exact
   current owner-issued target item/document and approval stage. Freeze the role that authorises
   that stage, not the first effective role in a fixed role list. A multi-role actor may not attach
   a Credit Manager or Sanction Committee condition/return to Company Secretary history.
4. Reconcile review-action audit/workflow/version identities before projecting blockers,
   conditions, or resolution. Tampered/duplicate/stale review evidence fails closed and cannot
   become approval truth; exact action replay remains zero-write and changed replay conflicts.
5. Preserve opaque commands, current renderer ownership, immutable signed-copy succession,
   redaction, sibling actions, one-refetch UI behavior, and the five existing trusted-browser
   screenshots without new styling or layout.

## Trusted Browser Acceptance

- Spec: `e2e/staff-documentation-workspace.e2e.spec.ts`
- Screenshot: `documentation-checklist-blockers.png`
- Screenshot: `documentation-security-workflow.png`
- Screenshot: `documentation-restricted-state.png`
- Screenshot: `documentation-final-approval.png`
- Screenshot: `documentation-checklist-narrow.png`

## Test Cases

- Reproduce the review probe: resolve a correction with a real uploaded successor, then change each
  file/checksum/action/audit/workflow/version/target fact independently; the blocker reappears and
  completion/approval/readiness remain denied with no new writes.
- Cover missing/duplicate predecessor or successor, cross-application/document resolution,
  replaced renderer, stale action identity, exact replay, changed replay, and two sequential valid
  corrections while retaining the complete immutable chain.
- Give actors primary and governed approval-authority role combinations and prove each
  return/condition freezes and projects only the current stage's authorising role. Wrong-stage,
  wrong-permission, stale-stage, and cross-user commands are nondisclosing and zero-write.
- Real-Django UI acceptance uploads and corrects a signed copy, refetches the durable blocker/state,
  and captures all five declared screenshots twice.

## Evidence Required

Failing-first copies of the architecture-review corrected-copy and stage-attribution probes;
sanitized chain/ledger manifests; focused backend/frontend results; twice-run browser artifacts;
full configured gates.

## Risk Level
High

## Acceptance Criteria

- No changed, ambiguous, or stale signed-copy evidence can clear a documentation correction.
- Every return and condition is durably attributed to the exact approval stage and authorising role.
- Existing renderer, action, download, redaction, pagination, and prototype contracts remain green.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Trusted-browser evidence saved
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit delegated to the orchestrator only after passing configured gates
