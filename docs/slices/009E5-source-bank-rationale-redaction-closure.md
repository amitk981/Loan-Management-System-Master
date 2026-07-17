# Slice 009E5: Source-Bank Rationale Redaction Closure

## Status
Complete

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Keep the reviewable source-bank reason required by 009E4 while making it impossible for formatted
bank identifiers or any repository field-encryption token to enter general audit/version evidence.

## Depends On
- 009E4

## Source / Review References
- `docs/source/auth-permissions.md` §§30.2-30.3 (CFG-001, AUD-005, AUD-006)
- `docs/source/data-model.md` §29.3
- `docs/source/codebase-design.md` §§39 and 42
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-17_210855_architecture_review`

## Concrete Requirements
1. Replace the source-bank module's local digit/marker checks with one shared safe-audit-text
   boundary. Reject contiguous or formatted account/card-like digit sequences and every canonical
   field-encryption token version/prefix, including tokens belonging to another bank or module.
2. Retain a bounded human-reviewable reason only when the safe-text boundary passes. Never retain
   rejected plaintext in governance, `VersionHistory`, `AuditLog`, workflow, exception, or
   validation output; return one generic safe validation message.
3. Preserve 009E4's exact reason/context digests, author/request/role/team/network attribution,
   no-false-approval rule, immutable predecessor history, unassigned Critical grant, and races.
4. Reuse the same shared validator for future general audit reasons without changing encryption,
   masking, or source-bank business authority.

## Test Cases
- Public activation/replacement rejects `1234-5678-9012`, spaced/slashed variants, unrelated
  `field:vN:` tokens, legacy encryption prefixes, current/other-bank tokens and hashes, controls,
  blanks, and oversize values with zero writes and no echo.
- Safe ordinary rationales remain exactly reviewable and reconcile through current/history/audit.
- Focused tests call the public source-bank interface; add a shared-validator table without testing
  private source-bank helpers. Preserve twice-run PostgreSQL first/replacement races.

## Runtime Capabilities

postgresql-five-race-acceptance

## Risk Level
High

## Acceptance Criteria
- General source-bank audit/version evidence cannot contain recognisable bank identifiers or field-
  encryption tokens, while safe reviewable reasons and all 009E4 integrity guarantees remain.

## Done Checklist
- [x] Execution plan written
- [x] Failing test written first and RED/GREEN evidence saved
- [x] Shared safe-text boundary implemented
- [x] Public, audit, history, and PostgreSQL tests passed
- [x] API contracts updated, if needed (no API shape changed)
- [x] Risk assessment, handoff, state, and evidence updated
- [x] Commit delegated to the orchestrator after gates
