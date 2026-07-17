# Slice 009E4: Source-Bank Rationale and Approval-Evidence Closure

## Status
Complete

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement
Epic file: `docs/epics/009-sap-loan-account-disbursement.md`

## Goal
Make every Critical source-bank activation/replacement retain its reviewable rationale honestly,
without presenting a request id or the acting provisioner as independent business approval.

## Depends On
- 009E3

## Runtime Capabilities

postgresql-five-race-acceptance

## Source / Review References
- `docs/source/auth-permissions.md` §§18, 30.2-30.3, and 31.1-31.2
- `docs/source/codebase-design.md` §§22, 38, and 42
- `docs/source/data-model.md` §§29-30 and 34
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-17_164724_architecture_review`
- Assumption A-126 in `docs/working/ASSUMPTIONS.md`

## Concrete Requirements
1. Retain a non-empty, bounded human-reviewable activation/replacement reason in protected current
   and historical governance evidence. A digest may supplement it for integrity but cannot replace
   CFG-001/§30.2's recoverable reason/comment. Reject blank, overlong, control-character, or
   sensitive bank-number/token content using the existing safe-text convention.
2. Keep the request identity, rationale, actor, role/team, request/network context, effective range,
   predecessor/successor, version, and audit identities distinct and exactly reconcilable. Changing
   any retained rationale or attribution must make current resolution fail closed.
3. Stop writing the HTTP/request identity into `VersionHistory.approval_reference` and stop setting
   the same provisioner as a claimed approver unless a separate current governed approval owner is
   supplied. The source does not name the source-bank provisioner/approver, so preserve A-126's
   unassigned Critical grant and record author/action truth honestly rather than inventing a role.
4. Preserve 009E3's database-required activation/deactivation evidence, immutable predecessor
   chain, encrypted/redacted bank facts, stable conflicts, and first-activation/replacement races.
   No role receives the activation grant by default.

## Test Cases
- Publicly activate and replace with distinct safe rationales; assert exact current/history/audit
  attribution and no plaintext bank account, ciphertext, capability, or unrelated identity data.
- Reject blank/oversized/unsafe rationale and prove no governance/version/audit writes.
- Mutate reason, digest, request identity, actor attribution, effective history, or a false approval
  claim one field at a time; current resolution fails without rewriting retained rows.
- Seed the production catalogue and prove no default role grant. Twice run the PostgreSQL five-
  caller first/replacement races and retain one complete, reviewable winner with clean losers.

## Evidence Required
Failing-first rationale/approval probes; sanitized activation/replacement manifests; catalogue proof;
twice-run PostgreSQL races; focused tests, Django check, migration sync, and full configured gates.

## Risk Level
High

## Acceptance Criteria
- Every accepted Critical source-bank change has a recoverable safe rationale and exact immutable
  audit/version attribution.
- Request ids and single-actor execution are never mislabeled as independent business approval.
- A-126 remains fail-closed on the unnamed provisioner while 009E3 concurrency/history guarantees
  remain intact.

## Done Checklist
- [x] Execution plan written
- [x] Tests written or updated
- [x] Code implemented
- [x] API contracts updated, if needed (no HTTP contract changed)
- [x] Database rules followed
- [x] Permissions tested
- [x] Audit events tested
- [x] Tests/typecheck/lint/build passed
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [x] Commit delegated to the orchestrator after gates
