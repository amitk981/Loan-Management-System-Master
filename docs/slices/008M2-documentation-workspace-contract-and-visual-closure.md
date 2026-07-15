# Slice 008M2: Documentation Workspace Contract and Visual Closure

## Status
Not Started

## Parent Epic
Epic 008: Documentation, Legal Documents, and Security Package

## Depends On
- 008L5
- 008M

## Runtime Capabilities

- `localhost-e2e-server`

## Goal

Turn the partial 008M projection into a source-faithful, genuinely reachable S26-S35 workspace,
restore the standard action contract and readable deep-module structure, and collect the visual
evidence that 008M declared but did not deliver.

## Source / Review References

- `docs/source/screen-spec.md` S26-S35 and §9.5
- `docs/source/api-contracts.md` §§26-28 and 44
- `docs/source/auth-permissions.md` §§22-23 and 37
- `docs/source/functional-spec.md` M06-FR-005 through M06-FR-019
- `docs/source/user-flows.md` §§18-20
- `docs/working/FRONTEND_DESIGN_RULES.md`
- `docs/slices/008M-documentation-hub-frontend-wiring.md`
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-16_023011_architecture_review`

## Concrete Requirements

1. Replace 008M's minified `staff_documentation_workspace.py`, compressed tests, and compressed
   frontend service/workspace hunks with readable deep-module interfaces. Stay below Ralph's diff
   limits through narrow ownership and reuse, never representation-density tricks or weaker tests.
2. Return every `available_actions` entry in the §44 shape: `action_code`, `label`, `enabled`,
   `disabled_reason`, `required_permission`, and optional `required_role`. Endpoint/method and
   server-derived option metadata may extend that object, but must not replace the shared vocabulary.
3. Derive actions from the same owner modules that execute them. Permission strings alone must not
   advertise authority. Include actually reachable S28-S34 generation, upload, signature/mismatch,
   stamp, notarisation, PoA, tri-party, SH-4, CDSL, cheque, bank-verification, correction, and
   verification actions where the current actor/state permits them; omit future recovery/closure
   actions and never turn a generic application navigation into claimed action completion.
4. Make every rendered action work through its supplied production endpoint and method using the
   existing Modal/Tabs/form patterns. Structured actions collect only source-required user input;
   canonical application/member/document/security ids remain server-owned. A success refetches one
   snapshot; 400/403/404/409 remains visible with no optimism or automatic retry.
5. Restore the S26 operational queue facts from one backend-owned projection: sanctioned amount,
   shareholding route, required set/status summary, PoA/tri-party/SH-4/CDSL/Term Sheet/Agreement/
   bank/checklist status, and current owner. Keep strict pagination; do not request page size 100 or
   present a partial page count as the complete queue.
6. Project a redacted audit/approval timeline and approver comments for S26/S35 using the existing
   `AuditTimeline`. Do not return terminal evidence, signer snapshots, request/network facts,
   hashes, ciphertext, storage keys, or internal action ids.
7. Keep status, Download, and every mutation independent in the main table and Document Pack modal.
   A downloadable pending document may still show its separately authorised Verify/Complete action;
   terminal status alone grants no action. Restricted content is absent and a direct content request
   returns `403/404` with no audit.
8. Render queue failure only as error, never alongside “All documentation is complete.” Add truthful
   loading, empty, unauthorized, validation, conflict, and success states using existing styling.
9. Add full staff download success/audit and denial tests: exact current capability succeeds once
   with one generic staff event; tamper, expiry, replacement, cross-user/application/item/action,
   and missing permission are nondisclosing and zero-audit.

## Trusted Browser Acceptance

- Spec: `e2e/staff-documentation-workspace.e2e.spec.ts`
- Screenshot: `documentation-checklist-blockers.png`
- Screenshot: `documentation-security-workflow.png`
- Screenshot: `documentation-restricted-state.png`
- Screenshot: `documentation-final-approval.png`

The spec must use a real authenticated Django server and persisted S26-S35 facts. It must execute at
least one real workflow action, verify a conflict remains non-optimistic, prove a restricted content
request reaches Django and is denied, and capture all four source-required states twice.

## Test Cases

- Backend action matrices compare projection to each owner module's public allow/deny result for
  Compliance, CS, Credit, Director, Finance, CFC, Auditor, and a permission-without-role actor.
- Frontend clicks every returned action family and asserts exact endpoint/method/payload/refetch.
- Queue pagination/error/empty tests and Document Pack Download+Verify coexistence tests pass.
- Staff download success/audit/tamper/expiry/replacement/cross-scope matrix is exact.
- Mock ratchet and recursive redaction scans remain green; all four screenshots are non-empty.

## 008L5 Completion Sharpening (2026-07-16)

- The S26 bank/checklist status and every related action must consume 008L5's reconciled current
  terminal-sanction bank fact. An application status label, a latest bank row whose retained
  approval-case/sanction-decision ids are stale, or an invalid current approval cycle must render a
  safe blocker and advertise no completion/verification action.
- Staff projections may show the borrower-safe bank outcome/status but must not expose either
  retained approval id, bank-decision evidence/digest, workflow/audit/version identity, or the
  internal terminal-sanction blocker code. Add the invalidated-cycle case to the existing recursive
  redaction and projection/action parity matrices.

## Evidence Required

Failing-first action/error/modal/download probes; focused backend/frontend results; full gates;
twice-run real-boundary browser logs; four screenshots; sanitized §44 workspace example; diff-limit
report showing readable source rather than minification.

## Risk Level
High

## Acceptance Criteria

- S26-S35 presents complete server-owned status and genuinely reachable role-correct actions.
- The shared action, error-state, pagination, redaction, and signed-download contracts are honored.
- Readable module/test structure and all mandatory visual evidence are delivered honestly.
- All configured gates pass.

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
