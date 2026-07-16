# Slice 009D3: Readiness Approval, Reader, and Boundary Closure

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement

## Depends On
- 008M6
- 009B3C
- 009D2

## Runtime Capabilities

none

## Goal

Make every readiness approval remain bound to exact current ordered completion evidence, restore all
source-authorised read roles with canonical loan scope, and keep orchestration behind the deep
disbursement-readiness boundary before payment initiation.

## Source / Review References

- `docs/source/codebase-design.md` §§14-16, 26-28, 36-37, and 42
- `docs/source/screen-spec.md` S27-S35 and S38
- `docs/source/api-contracts.md` §§6-8 and 31.1
- `docs/source/auth-permissions.md` §§15.3, 15.6-15.8, 19.3, 20.2, 26.5, and 37
- `docs/source/data-model.md` §§18-19, 27.3, 28-30, and 34
- `docs/source/functional-spec.md` M06-FR-019, M07-FR-010, and M08-FR-001 through M08-FR-004
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-16_213746_architecture_review`

## Concrete Requirements

1. Reconcile each Company Secretary, Credit Manager, and Sanction Committee action against the
   exact currently valid ordered item-completion actions, not all historical action ids. Preserve
   order and require singular matching approval audit/workflow/version rows; duplicate, missing,
   reordered, stale, unrelated, or changed ledgers fail that stage and every downstream stage.
2. Re-evaluate current completion evidence for approval readiness through the same terminal legal/
   security/signed-copy decisions as `documentation_complete`. A changed renderer, corrected copy,
   item action, terminal evidence, or completion body must make all approvals that consumed it stale,
   even if the checklist status and approval foreign keys remain terminal.
3. Evaluate the exact required current signer set for Term Sheet, Loan Agreement, PoA, tri-party,
   SH-4, and applicable documents. An empty/missing required signer set, stale document, wrong
   signer, open/contradictory mismatch, or changed resolution evidence must fail the appropriate
   signature/documentation checks; never rely on `all([])` as evidence.
4. Restore the source read matrix: active persisted Senior Manager Finance, CFC, Credit Manager,
   CFO, and Internal Auditor users with `finance.disbursement.readiness` receive only their §19.3/
   §26.5 canonical loan scope. Senior Finance uses the newest SAP assignment; pre-009E CFC remains
   absent; Credit Manager uses its active-loan/monitoring domain; CFO uses portfolio detail; Auditor
   uses audit-readonly scope. Permission/role alone, application origination assignment, and missing
   or cross-object ids remain nondisclosing.
5. Keep `disbursements.modules.disbursement_readiness` as the small public composition boundary.
   Cross-owner legal/security evidence may use the established typed `processes` coordinator, but
   readiness-specific pass-through APIs and policy must not accumulate in that coordinator or create
   a second public readiness owner.
6. Preserve 23 ordered checks, exact 009B3C SAP decision, honest A-126 source-bank blocker, safe
   reasons, read-only/zero-write behavior, standard envelope, and full current-owner query bound.

## Test Cases

- Reproduce the review probe: after a genuine all-pass owner fixture, change one completion version
  body; `documentation_complete` and all three approvals fail. Repeat for order, duplicate sibling
  audit/workflow/version rows, action identities, renderer/current signed copy, and security facts.
- Remove each required current signer and prove the named signature/documentation check fails;
  cover wrong, stale, duplicate, open mismatch, resolved mismatch, and inapplicable document paths.
- Public scope matrix covers Senior Finance, pre/post-009E-shaped CFC seam, Credit Manager, CFO,
  Auditor, wrong role/grant, inactive user, application intake owner, cross-account/member/application,
  and absent id without leaked existence or writes.
- Public real-owner success reaches only A-126, then a governed source-bank decision produces all 23
  passes without mocking legal, security, approval, SAP, or loan owners. Capture query count on this
  complete path rather than only an incomplete fixture.
- Dependency tests assert the one public disbursement-readiness interface and the established
  source-compatible cross-owner direction without source-substring-only behavioral claims.

## Evidence Required

Failing-first approval/reader/signature probes; exact ordered-ledger and role-scope matrices;
genuine all-pass/A-126 responses; query and zero-write proof; focused tests and full configured gates.

## Risk Level
High

## Acceptance Criteria

- No approval or signature check passes without exact current ordered owner evidence.
- Every source-authorised readiness reader receives only its canonical loan scope.
- Payment initiation can consume one deep deterministic secret-free read-only readiness decision.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested
- [ ] Audit events verified zero-write
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit delegated to the orchestrator only after passing configured gates
