# Slice 009D2: Readiness Evidence and Loan-Scope Closure

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement

## Depends On
- 009D
- 009B3

## Runtime Capabilities

none

## Goal

Make every 009D pass depend on exact current owner-reconciled evidence and source-defined loan-
account scope so mutable status fields, open mismatches, forged ledger links, or origination
assignment cannot authorize payment readiness.

## Source / Review References

- `docs/source/codebase-design.md` §§14-16, 22, 26-28, 36-37, and 42
- `docs/source/screen-spec.md` S27-S35
- `docs/source/api-contracts.md` §§6-8 and 31.1
- `docs/source/auth-permissions.md` §§15.6-15.7, 19.2-19.4, 23, 26.5, and 37
- `docs/source/data-model.md` §§18-19, 28-30, and 34
- `docs/source/functional-spec.md` M06-FR-019, M07-FR-010, M08-FR-001 through M08-FR-004
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-16_143718_architecture_review`

## Concrete Requirements

1. Replace legal readiness's direct checklist/item status test with the checklist owner's exact
   current reconciliation. Every required-and-applicable item needs its one canonical completion
   action, audit, workflow, version, current renderer, and exact current terminal evidence; an
   inapplicable item does not block merely because its stored completion status is pending.
2. Reconcile Company Secretary, Credit Manager, and Sanction Committee approvals through their full
   canonical action/evidence identities and current ordered checklist facts. Non-null foreign keys,
   copied status, unrelated/duplicate ledgers, bulk updates, or a stale approval cycle never pass.
3. Evaluate all current signature rows. Any open, unverified, unresolved, stale-document, wrong-
   signer, contradictory, or duplicate mismatch fails `signature_mismatch_resolved`; filtering a row
   because verifier/time is absent is forbidden.
4. Replace shallow security status checks with the existing coordinated terminal-evidence contract
   used by checklist completion. PoA exact ₹500 stamp/notary/signatures/maker-checker/checksum/event,
   SH-4 custody, CDSL acceptance/future-share flag, and blank-cheque custody/bank linkage must all
   reconcile; conditional SH-4/CDSL paths pass only when owner applicability says not required.
5. Introduce one loan-owner read-scope decision for readiness based on auth §§19.3/26.5 and current
   loan/disbursement state. Do not call application-origination ownership or make a CFC the
   application's `received_by_user`. Missing ids and denied Senior Manager Finance/CFC contexts stay
   indistinguishable and zero-write.
6. Preserve all 23 ordered checks, safe blocker reasons, query bound, read-only behavior, current SAP
   owner decision, and honest A-126 source-bank failure. 009E must consume only this corrected exact
   decision; no payment/CFC/activation truth is added here.

## Test Cases

- Public real-owner tests start from a fully terminal source-owned fixture, assert all checks except
  the known A-126 source-bank blocker, then inject the governed source-bank decision and prove a
  genuine all-pass response without mocking any readiness owner.
- Mutate each checklist item/status/link/action/audit/workflow/version/current renderer and each
  approval/signature/security evidence component independently; every case fails exactly its named
  check and leaves all ledgers unchanged. Include required-but-inapplicable pending items.
- Loan scope tests cover persisted Senior Manager Finance and CFC source states, wrong role/grant,
  unrelated application assignment, cross-account/member/application, inactive user, and absent id;
  no fixture may assign `received_by_user` merely to grant loan access.
- Keep the isolated coordinator boolean matrix as a small unit test, but it cannot substitute for the
  public real-owner success/failure matrix. Architecture tests exercise public interfaces and
  dependency direction rather than source substrings.

## Evidence Required

Failing-first architecture-review probes; sanitized genuine ready/all-blocked examples; exact
owner-evidence mutation matrix; loan-scope matrix; query/zero-write results; full configured gates.

## Risk Level
High

## Acceptance Criteria

- No copied status, missing/forged/duplicate evidence, open mismatch, or shallow security row can
  become a readiness pass.
- Readiness uses canonical loan scope, not application origination assignment.
- The exact §31.1 contract remains complete, deterministic, secret-free, and read-only.

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
