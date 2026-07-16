# Slice 008M3: Documentation Workspace Executable Action Closure

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package

## Depends On
- 008M2

## Runtime Capabilities

- `localhost-e2e-server`

## Goal

Make every S26-S35 action advertised by the staff documentation workspace complete and executable
through its owning public workflow, while keeping all canonical object identities server-owned and
rendering every independently authorised mutation in both the checklist and Document Pack.

## Source / Review References

- `docs/source/screen-spec.md` S26-S35
- `docs/source/api-contracts.md` §§6-8, 26-28, and 44
- `docs/source/auth-permissions.md` §§22-23 and 37
- `docs/source/codebase-design.md` §§14-15, 23, 27, 36-37, and 42
- `docs/source/functional-spec.md` M06-FR-005 through M06-FR-019
- `docs/slices/008M2-documentation-workspace-contract-and-visual-closure.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-16_072819_architecture_review`

## Concrete Requirements

1. Replace actor-only action advertisement with one owner-issued decision/command contract per
   action. An action may be `enabled: true` only when the same locked current facts and actor would
   let its public write boundary proceed; otherwise omit it or return the §44 disabled reason.
2. Close the independently reproduced Loan Agreement case: do not advertise `complete_item` while
   signature/stamp/notary/current-document evidence is incomplete. Add parity cases for every
   checklist item and approval stage, including stale renderer, invalid bank cycle, and mismatches.
3. Add the source-required reachable upload/re-upload, correction/return, and S35 condition/return
   action families. Use existing owner routes or one narrow process coordinator; do not invent a
   parallel document/security state or generic navigation substitute.
4. Keep canonical application/member/nominee/witness/document/template/security/bank ids out of
   caller-controlled `fixed_payload`. The workspace action boundary resolves and locks them again;
   the browser submits only source-required user input and an opaque current action identity.
5. Render every `available_actions` entry in the main checklist and Document Pack, alongside an
   independent Download control. Preserve source order and stable unique action keys; no `[0]`
   selection or one-button test fixture may hide sibling signature/stamp/notary/complete actions.
6. Make success refetch once and keep 400/403/404/409 non-optimistic. Unknown, stale, tampered,
   cross-user/application/item/action identities are nondisclosing and zero-write.
7. Extend real-Django trusted-browser acceptance to click an enabled action through the UI, exercise
   upload/correction plus a multi-mutation Document Pack row, prove a rejected action stays visible,
   and recapture all four 008M2 screenshots twice using existing prototype patterns only.

## Trusted Browser Acceptance

- Spec: `e2e/staff-documentation-workspace.e2e.spec.ts`
- Screenshot: `documentation-checklist-blockers.png`
- Screenshot: `documentation-security-workflow.png`
- Screenshot: `documentation-restricted-state.png`
- Screenshot: `documentation-final-approval.png`

## Test Cases

- The architecture-review action-parity probe passes with no advertised/execution disagreement.
- Backend matrices compare every projected action to the exact owner decision and public result for
  Compliance, CS, Credit, Director, Finance, CFC, Auditor, and permission-without-role actors.
- Frontend tests render and execute every sibling action, upload/correction, download coexistence,
  field validation, tampered action identity, conflict, and one-refetch success.
- Trusted-browser runs use a real staff session and Django persistence, click real UI controls, and
  produce the four declared screenshots twice without intercepting owned API calls.

## Evidence Required

Failing-first copies of the architecture-review probe and modal/upload regressions; sanitized §44
examples; focused backend/frontend results; twice-run trusted-browser logs and screenshots; full
configured gates.

## Risk Level
High

## Acceptance Criteria

- Every displayed action is complete, current, server-owned, role-correct, and executable.
- Upload/correction and every sibling mutation are reachable in the approved existing UI patterns.
- Stale/tampered/denied actions are nondisclosing and zero-write; all configured gates pass.

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
- [ ] Commit delegated to the orchestrator only after passing configured gates
