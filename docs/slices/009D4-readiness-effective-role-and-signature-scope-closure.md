# Slice 009D4: Readiness Effective-Role and Signature-Scope Closure

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement

## Depends On
- 008M7
- 009D3

## Runtime Capabilities

none

## Goal

Apply the source readiness reader matrix to active governed approval-authority roles and keep
signature readiness scoped to the exact current applicable documents it names.

## Source / Review References

- `docs/source/auth-permissions.md` §§15.6-15.8, 19.3, 26.5, and 37
- `docs/source/codebase-design.md` §§14-16, 27, 36-37, and 42
- `docs/source/screen-spec.md` S32-S35 and S38
- `docs/source/functional-spec.md` M06-FR-019 and M08-FR-001 through M08-FR-004
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-17_075837_architecture_review`

## Concrete Requirements

1. Resolve readiness roles through the central active effective-role boundary, including a valid
   `approval_authority_type`, rather than `User.role_codes()` alone. Require the explicit readiness
   permission and evaluate the union of each effective source role's canonical loan scope; fixed
   `if/elif` precedence must not make a multi-role actor narrower or broader accidentally.
2. Preserve Senior Manager Finance newest-SAP-assignee scope, pending initiated-disbursement CFC
   scope, Credit active-loan/monitoring scope, CFO portfolio-detail scope, and explicit Auditor
   read-only scope. A governed role is effective only while its catalogue role and user are active;
   a free-form authority string, role alone, or permission alone grants nothing.
3. Limit legal signature reconciliation to the latest current applicable Term Sheet, Loan
   Agreement, PoA, tri-party agreement, and SH-4 documents. A legitimate signature on another
   document type must not fail readiness; any extra/wrong/duplicate signer on a required document
   must still fail.
4. Continue to require the exact approval-owned Term Sheet signer set and current mismatch evidence.
   Consume 008M7's current correction-tail decision and preserve all 23 check codes/order, safe
   reasons, zero-write reads, source envelope, and query bound.

## Test Cases

- Reproduce the review probes: a primary non-finance user with active governed CFO authority and an
  explicit readiness grant receives CFO-scoped access; inactive/unknown authority and missing grant
  are denied. Repeat for governed CFC and multi-role Senior Finance/CFC precedence.
- Add a valid signature on `final_checklist` or another non-readiness document after a genuine
  all-pass fixture; readiness remains unchanged. Add an extra/wrong signer to each required current
  document; the signature/documentation checks fail.
- Prove cross-account/member/application scope, intake assignment, archived Credit state, pre-009E
  CFC, stale correction tail, and changed mismatch evidence remain nondisclosing or failed with no
  writes.

## Evidence Required

Failing-first governed-role and unrelated-signature probes; role/scope matrix; exact signer matrix;
genuine all-owner readiness response; query/zero-write proof; focused tests and full configured gates.

## Risk Level
High

## Acceptance Criteria

- Every active source-authorised primary or governed readiness role receives only its canonical scope.
- Unrelated signature history cannot poison readiness, while required-document signer drift fails closed.
- Readiness remains one deterministic, secret-free, read-only 23-check decision.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Permissions tested
- [ ] Audit events verified zero-write
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit delegated to the orchestrator only after passing configured gates
