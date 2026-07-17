# Slice 008M7: Current Correction Tail Closure

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package

## Depends On
- 008M6

## Runtime Capabilities

none

## Goal

Keep a documentation correction resolved only while the current sole signed-copy tail retains an
exact, coherent link to that correction; a later unlinked re-upload must never inherit resolution
silently.

## Source / Review References

- `docs/source/codebase-design.md` §§14, 27, 36-37, and 42
- `docs/source/api-contracts.md` §§6-8, 26-28, and 44
- `docs/source/functional-spec.md` M06-FR-018 and M06-FR-019
- `docs/source/screen-spec.md` S26-S27 and S35
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-17_075837_architecture_review`

## Concrete Requirements

1. Change the legal-owner correction decision so the resolving signed copy must be the current sole
   tail, not merely any historical member of a coherent predecessor chain. The tail must retain the
   exact correction id and current file/checksum/action/audit/workflow/version facts required by
   008M6.
2. Define one explicit immutable behavior for a later ordinary upload: either inherit and retain the
   exact still-current correction identity as part of the new successor evidence, or leave the old
   correction open. A bare successor with `resolves_review_action_id = null` must never keep the
   prior correction resolved.
3. Make `has_open_blocker`, workspace queue/detail, item completion, ordered approvals, and
   disbursement readiness consume the same tail decision. Preserve all historical copies and review
   actions; do not rewrite or delete the earlier resolution.
4. Preserve cross-application/document rejection, exact replay, changed replay conflict, current
   renderer ownership, signed downloads, redaction, and the existing workspace UI composition.

## Test Cases

- Reproduce the architecture probe: initial copy -> correction -> linked corrected copy -> ordinary
  unlinked successor. The correction becomes open and completion/approval/readiness all fail, or the
  successor explicitly inherits the exact resolution link and all owner ledgers prove that fact.
- Mutate the latest tail's resolution id, predecessor, file/checksum, uploader, action, upload/legal
  audit, workflow, or version one field at a time; every consumer fails closed with no writes.
- Cover two sequential corrections, an ordinary successor before any correction, exact replay,
  changed replay, ambiguous tails, and a later renderer generation.

## Evidence Required

Failing-first copy of the architecture probe; sanitized tail/resolution manifest; focused legal,
checklist, approval, and readiness tests; Django check and migration sync; full configured gates.

## Risk Level
High

## Acceptance Criteria

- No historical corrected copy can clear a correction after a different current tail replaces it.
- Every Stage-4 and readiness consumer agrees on the same exact current correction decision.
- No production history, renderer, download, or UI contract is weakened.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit delegated to the orchestrator only after passing configured gates
